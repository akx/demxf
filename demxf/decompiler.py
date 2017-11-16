import re
from collections import defaultdict

from demxf.toposort import CycleError, topological_sort

aesthetic_keys = {
    'background',
    'bgcolor',
    'bgcolor2',
    'bgfillcolor_angle',
    'bgfillcolor_autogradient',
    'bgfillcolor_color',
    'bgfillcolor_color1',
    'bgfillcolor_color2',
    'bgfillcolor_proportion',
    'bgfillcolor_type',
    'bgmode',
    'bgoncolor',
    'blinkcolor',
    'border',
    'bordercolor',
    'checkedcolor',
    'clickthrough',
    'color',
    'curvecolor',
    'enablehscroll',
    'enablevscroll',
    'fontface',
    'fontname',
    'fontsize',
    'gradient',
    'gridcolor',
    'hidden',
    'htabcolor',
    'htricolor',
    'ignoreclick',
    'markercolor',
    'needlecolor',
    'offcolor',
    'offset',
    'outlinecolor',
    'patching_rect',
    'presentation',
    'presentation_rect',
    'rounded',
    'selectioncolor',
    'slidercolor',
    'style',
    'tabcolor',
    'textcolor',
    'textoncolor',
    'textovercolor',
    'tricolor',
    'uncheckedcolor',
    'usebgoncolor',
}

nonprinted_keys = {
    'data',
    'id',
    'maxclass',
    'numinlets',
    'numoutlets',
    'outlettype',
    'saved_attribute_attributes',
    'saved_object_attributes',
}


def filter_keys(d, to_remove):
    return {k: v for (k, v) in d.items() if k not in to_remove}


def identifierify(value):
    value = re.sub('[^a-z0-9_]+', '', value.replace(' ', '_'), flags=re.I)
    if not value:
        return None
    if not value[0].isalpha():
        value = '_' + value
    return value


def remove_aesthetics(box):
    return {k: v for (k, v) in box.items() if not (k in aesthetic_keys or k.endswith('color'))}


def divine_id(box, id_prefix=''):
    num_id = box['id'].replace('obj-', '')
    t_id = get_box_printable_class(box)
    if t_id == 'newobj' and 'text' in box:
        t_id = (identifierify(box['text'].lower()) or t_id)
    return '%s%s_%s' % (id_prefix, t_id, num_id)


def get_box_printable_class(box):
    t_id = box['maxclass']
    if t_id == 'newobj':
        if box['text'].startswith('r '):
            t_id = 'receive'
        elif box['text'].startswith('s '):
            t_id = 'send'
        elif box['text'].isalnum():
            t_id = box['text']
    t_id = t_id.replace('~', '_sigl')
    return t_id


class BasePatchDecompiler:
    def __init__(self, id_prefix=''):
        self.id_prefix = id_prefix

    def initialize(self, content):
        if len(content) == 1 and 'patcher' in content:
            content = content['patcher']
        content = content.copy()
        boxes = {b['box']['id']: b['box'] for b in content.pop('boxes', [])}
        lines = [(l['patchline']['source'], l['patchline']['destination']) for l in content.pop('lines', [])]
        divined_id_map = {id: divine_id(box, self.id_prefix) for (id, box) in boxes.items()}
        lines_by_source_id = defaultdict(list)
        for line in lines:
            source, dest = line
            lines_by_source_id[source[0]].append(line)
        topo_sort_graph = {
            source_id: set(line[1][0] for line in lines)
            for (source_id, lines)
            in lines_by_source_id.items()
        }
        try:
            sort_order = list(topological_sort(topo_sort_graph))
        except CycleError:
            sort_order = []
        self.boxes = boxes
        self.lines = lines
        self.divined_id_map = divined_id_map
        self.lines_by_source_id = lines_by_source_id
        self.sort_order = sort_order
        self.subpatchers = []
        for box in boxes.values():
            if 'patcher' in box:
                self.subpatchers.append(box.pop('patcher'))
                box['subpatcher_id'] = (len(self.subpatchers) - 1)
                box['maxclass'] = '_subpatcher'

    def _sort_key(self, pair):
        id, box = pair
        if id in self.sort_order:
            return (False, -self.sort_order.index(id))
        else:
            return (True, self.divined_id_map.get(id, id))

    def dump(self):
        for id, box in sorted(self.boxes.items(), key=self._sort_key):
            self.process_box(box)

        for id, subpatcher in enumerate(self.subpatchers):
            self.process_subpatcher(id, subpatcher)

    def process_box(self, box):
        pass

    def process_subpatcher(self, id, subpatcher):
        pass


class PatchDecompiler(BasePatchDecompiler):
    def process_box(self, box):
        id = box['id']
        box = box.copy()
        if box['maxclass'] == 'comment':
            print('# (comment) ' + box['text'])
            return
        type_comment = '{n_in} in, {n_out} out ({types})'.format(
            n_in=box.get('numinlets', 0),
            n_out=box.get('numoutlets', 0),
            types=', '.join(s or '?' for s in box.get('outlettype', [])),
        )
        printable_class = get_box_printable_class(box)
        filtered_box = filter_keys(remove_aesthetics(box), nonprinted_keys)
        formatted_keys = ['{}={}'.format(key, repr(value)) for (key, value) in sorted(filtered_box.items())]

        if len(formatted_keys) <= 2 or len(''.join(formatted_keys)) <= 79:
            print('{id} = {cls}({keys})'.format(
                id=self.divined_id_map[id],
                cls=printable_class,
                keys=', '.join(formatted_keys),
            ))
        else:
            print('{id} = {cls}('.format(
                id=self.divined_id_map[id],
                cls=printable_class,
            ))
            for line in formatted_keys:
                print('  {line},'.format(line=line))
            print(')')
        outlet_types = dict(enumerate(box.get('outlettype', [])))
        for line in sorted(self.lines_by_source_id[id]):
            (source_id, source_pin), (dest_id, dest_pin) = line
            print('{source_id}[{source_pin}] = {dest_id}[{dest_pin}]  # type = {type}'.format(
                source_id=self.divined_id_map[source_id],
                source_pin=source_pin,
                dest_id=self.divined_id_map[dest_id],
                dest_pin=dest_pin,
                type=(outlet_types.get(source_pin) or '?'),
            ))

    def process_subpatcher(self, id, subpatcher):
        print('# -- subpatcher {} --'.format(id))
        sub_id_prefix = self.id_prefix + 'sp{}_'.format(id)
        subdecompiler = self.__class__(id_prefix=sub_id_prefix)
        subdecompiler.initialize(subpatcher)
        subdecompiler.dump()


def decompile_patch(patcher, id_prefix=''):
    decomp = PatchDecompiler(id_prefix)
    decomp.initialize(patcher)
    decomp.dump()


def decompile_patchverse(patchverse):
    for patch_name, patch in patchverse.items():
        prefix = re.sub('[^a-z0-9_]+', '', patch_name.split('.')[0], flags=re.I)
        if not prefix[0].isalpha():
            prefix = 'p' + prefix
        print('# ===')
        print('# === ' + patch_name)
        print('# ===')
        decompile_patch(patch, id_prefix=prefix + '_')
