from crawler import Crawler
from python_parser import PythonASTParser
import sys
import json

cl = Crawler(sys.argv[1])
cl.loadfile_ignore_abspath("./ignore_abs.txt")
cl.loadfile_ignore_name("./ignore_name.txt")
result_all = []
for file in cl.search():
    print(file)
    astp = PythonASTParser(str(file))
    result_all.extend(astp.list())

with open("result.json", "w", encoding="utf8") as f:
    json.dump(result_all, f, ensure_ascii=False)