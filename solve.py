from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("ssc"),
    autoescape=select_autoescape()
)
