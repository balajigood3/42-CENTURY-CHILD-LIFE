import ast,io,json,re
from zipfile import ZipFile,ZIP_DEFLATED
def analyze_source(source):
 if not isinstance(source,str): raise ValueError("Source must be text")
 if len(source.encode("utf-8"))>250000: raise ValueError("Source exceeds 250 KB")
 try: tree=ast.parse(source)
 except SyntaxError as e: raise ValueError(f"Syntax error at line {e.lineno}: {e.msg}") from e
 funcs=[];classes=[];imports=[]
 for n in tree.body:
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
   args=[a for a in n.args.args if a.arg not in {"self","cls"}]
   funcs.append({"name":n.name,"kind":"async" if isinstance(n,ast.AsyncFunctionDef) else "function","line":n.lineno,
    "docstring":" ".join((ast.get_docstring(n) or "").split()),
    "parameters":[{"name":a.arg,"type":ast.unparse(a.annotation) if a.annotation else "Any"} for a in args],
    "returns":ast.unparse(n.returns) if n.returns else "Any"})
  elif isinstance(n,ast.ClassDef):
   classes.append({"name":n.name,"line":n.lineno,"docstring":" ".join((ast.get_docstring(n) or "").split()),
    "methods":[x.name for x in n.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))]})
  elif isinstance(n,(ast.Import,ast.ImportFrom)): imports.append(ast.unparse(n))
 return {"module_docstring":" ".join((ast.get_docstring(tree) or "").split()),"functions":funcs,"classes":classes,"imports":imports,"line_count":len(source.splitlines())}
def generate_documentation(source,module_name="python_project"):
 if not re.fullmatch(r"[A-Za-z0-9_. -]{1,80}",module_name.strip()): raise ValueError("Invalid project name")
 a=analyze_source(source);name=module_name.strip()
 readme=f"# {name}\n\n{a['module_docstring'] or 'Documentation generated from Python source using AST inspection.'}\n\n## Summary\n\n- Lines: {a['line_count']}\n- Classes: {len(a['classes'])}\n- Functions: {len(a['functions'])}\n\nSee API_REFERENCE.md and ARCHITECTURE.md.\n"
 api=f"# {name} — API Reference\n\n## Classes\n\n"
 api+="\n".join(f"### `{c['name']}` (line {c['line']})\n\n{c['docstring'] or 'No class docstring.'}\n\nMethods: {', '.join(c['methods']) or 'None'}\n" for c in a["classes"]) or "No classes found.\n"
 api+="\n## Functions\n\n"
 api+="\n".join(f"### `{f['name']}({', '.join(p['name']+': '+p['type'] for p in f['parameters'])}) -> {f['returns']}`\n\n- Kind: {f['kind']}\n- Line: {f['line']}\n- Description: {f['docstring'] or 'No docstring provided.'}\n" for f in a["functions"]) or "No functions found.\n"
 arch=f"# Architecture Notes — {name}\n\n## Imports\n"+("\n".join("- `"+x+"`" for x in a["imports"]) or "- No imports")+"\n\n## Classes\n"
 arch+="\n".join("- `"+c["name"]+"`: "+(", ".join(c["methods"]) or "no methods") for c in a["classes"]) or "- No classes"
 arch+="\n\n## Functions\n"+"\n".join("- `"+f["name"]+"` ("+f["kind"]+") at line "+str(f["line"]) for f in a["functions"])
 arch+="\n\nNote: syntax-level inventory only; runtime behavior and call graphs are not inferred.\n"
 return {"README.md":readme,"API_REFERENCE.md":api,"ARCHITECTURE.md":arch,"analysis":a,"summary":{"functions":len(a["functions"]),"classes":len(a["classes"]),"lines":a["line_count"]}}
def make_zip(r):
 b=io.BytesIO()
 with ZipFile(b,"w",ZIP_DEFLATED) as z:
  for n in ("README.md","API_REFERENCE.md","ARCHITECTURE.md"): z.writestr(n,r[n])
  z.writestr("analysis.json",json.dumps(r["analysis"],indent=2));z.writestr("SUMMARY.json",json.dumps(r["summary"],indent=2))
  z.writestr("GENERATOR_NOTES.txt","Review generated documentation and add project-specific setup, examples, deployment, and operational details.\n")
 return b.getvalue()
