from edsnlp.core import registry
from edsnlp.pipelines.misc.tables import TablesMatcher
from edsnlp.utils.deprecation import deprecated_factory

DEFAULT_CONFIG = dict(
    tables_pattern=None,
    sep_pattern=None,
    attr="TEXT",
    ignore_excluded=True,
)

create_component = TablesMatcher
create_component = deprecated_factory(
    "tables",
    "eds.tables",
    assigns=["doc.spans", "doc.ents"],
)(create_component)
create_component = registry.factory.register(
    "eds.tables",
    assigns=["doc.spans", "doc.ents"],
)(create_component)