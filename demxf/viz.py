import graphviz

from demxf.decompiler import (
    BasePatchDecompiler,
    filter_keys,
    get_box_printable_class,
    nonprinted_keys,
    remove_aesthetics,
)


class PatchGrapher(BasePatchDecompiler):
    def initialize(self, content):
        super(PatchGrapher, self).initialize(content)
        self.graph = graphviz.Digraph()

    def process_box(self, box):
        id = box['id']
        box = box.copy()
        if box['maxclass'] == 'comment':
            return
        d_id = self.divined_id_map[id]
        filtered_box = filter_keys(remove_aesthetics(box), nonprinted_keys)
        formatted_keys = ['{}={}'.format(key, repr(value)) for (key, value) in sorted(filtered_box.items())]
        if box['maxclass'] == 'newobj' and len(filtered_box) == 1:
            label = filtered_box['text']
        else:
            label = '{name}\n{keys}'.format(
                name=get_box_printable_class(box),
                keys='\n'.join(l[:200] for l in formatted_keys),
            )
        self.graph.node(d_id, label, shape='box', style=('dotted' if box.get('hidden') else ''))
        outlet_types = dict(enumerate(box.get('outlettype', [])))
        lines_from_here = self.lines_by_source_id[id]
        for line in sorted(lines_from_here):
            (source_id, source_pin), (dest_id, dest_pin) = line
            type = outlet_types.get(source_pin) or ''
            source_outlets = box['numoutlets']
            dest_inlets = self.boxes[dest_id]['numinlets']
            if source_outlets > 1 or dest_inlets > 1:
                label = '%s %d:%d' % (type, source_pin + 1, dest_pin + 1)
            else:
                label = type
            self.graph.edge(
                tail_name='{id}'.format(id=self.divined_id_map[source_id], pin=source_pin),
                head_name='{id}'.format(id=self.divined_id_map[dest_id], pin=dest_pin),
                label=label,
            )

    def dump(self):
        super(PatchGrapher, self).dump()
        return self.graph
