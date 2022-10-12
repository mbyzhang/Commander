import re

from werkzeug.exceptions import NotFound

from flask import Flask, request, redirect, url_for, render_template
from dataclasses import dataclass
from datalite import datalite
from datalite.fetch import fetch_all
from datalite.datalite_decorator import remove_from
from string import Template
from urllib.parse import quote

@datalite(db_path="rules.db")
@dataclass
class Rule:
    name: str
    pattern: str
    template: str
    priority: int = 0
    quote_url: bool = True

app = Flask(__name__)

@app.route("/s")
def handle_search():
    cmd = request.args.get("q")
    rules = fetch_all(Rule, element_count=0)

    for rule in sorted(rules, key=lambda x: x.priority):
        if match := re.fullmatch(rule.pattern, cmd):
            groups = {
                "_" + str(k + 1): v
                for k, v in enumerate(match.groups())
            }

            groups.update(match.groupdict())

            if rule.quote_url:
                groups = {
                    k: quote(v, safe="")
                    for k, v in groups.items()
                }

            url = Template(rule.template).substitute(groups)
            return redirect(url)

    raise NotFound(f"{cmd} does not match any rules")

@app.route("/")
def handle_home():
    return redirect(url_for("handle_rules_get"))

@app.route("/rules", methods=["GET"])
def handle_rules_get():
    rules = fetch_all(Rule, element_count=0)
    return render_template("rules.html", rules=rules)
    
    
@app.route("/rules", methods=["POST"])
def handle_rules_post():
    if request.form.get("delete"):
        # delete the rule specified
        obj_id = request.form.get("id", type=int)
        print(f"Removing {obj_id}")
        remove_from(Rule, obj_id)
    else:
        # create a rule
        rule = Rule(
            name=request.form.get("name", "Untitled"),
            pattern=request.form.get("pattern"),
            template=request.form.get("template"),
            priority=request.form.get("priority", type=int),
            quote_url=request.form.get("quote_url", type=bool),
        )
        rule.create_entry()
    
    return redirect(url_for("handle_rules_get"))