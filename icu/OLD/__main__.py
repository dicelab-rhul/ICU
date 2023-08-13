from . import run, get_parser

parser = get_parser()

args = parser.parse_args()
run(**args.__dict__)