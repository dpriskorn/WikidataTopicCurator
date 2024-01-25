import logging
import os
from typing import List, Optional
from urllib.parse import quote, unquote

from flask import Flask, render_template, request, redirect, jsonify
from markupsafe import escape

from models.articles import Articles
from models.cirrussearch import Cirrussearch
from models.parameters import Parameters
from models.topic import TopicItem

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

invalid_format = f"Not a valid QID, format must be 'Q[0-9]+'"


def build_term_row(term: str, source: str):
    return f"""
    <tr>
        <td>                    
            <input type="checkbox" name="terms" value="{term}" checked=true>
        </td>
        <td>                    
            {term}
        </td>
        <td>                    
            <span class="source">{source}</span>
        </td>
    </tr>
    """


def build_terms_html(user_terms: List[str], topic: Optional[TopicItem] = None) -> str:
    """Build the table row html"""
    html_lines = list()
    if topic is not None:
        html_lines.append(build_term_row(term=topic.label, source="label"))
        for term in topic.aliases:
            html_lines.append(build_term_row(term=term, source="alias"))
    for term in user_terms:
        html_lines.append(build_term_row(term=term, source="user"))
    return "\n".join(html_lines)


@app.route("/", methods=["GET", "POST"])
def index():
    """We either get a get request or a post request
    If we get arguments, prefill the template"""
    if request.method == "POST":
        qid = escape(request.form.get("qid", ""))
        limit = escape(request.form.get("limit", "10"))
        cs = escape(request.form.get("cs", ""))
        csa = escape(request.form.get("csa", ""))
        terms = [escape(term) for term in request.form.getlist("terms")]
    else:
        qid = escape(request.args.get("qid", ""))
        limit = escape(request.args.get("limit", "10"))
        cs = escape(request.args.get("cs", ""))
        csa = escape(request.args.get("csa", ""))
        terms = [escape(term) for term in request.args.getlist("terms")]
    if qid:
        topic = TopicItem(qid=qid)
        if not topic.is_valid:
            return jsonify(error=invalid_format), 400
        return render_template(
            "index.html",
            qid=qid,
            limit=limit,
            cs=cs,
            csa=csa,
            terms_html=build_terms_html(user_terms=terms, topic=topic),
        )
    else:
        return render_template(
            "index.html",
            qid=qid,
            limit=limit,
            cs=cs,
            csa=csa,
            terms_html=build_terms_html(user_terms=terms),
        )


@app.route("/articles", methods=["GET"])
def articles():
    qid = escape(request.args.get("qid", ""))
    if not qid:
        return jsonify(f"Got no QID")
    limit_param = escape(request.args.get("limit", "10"))
    terms = escape(request.args.getlist("terms"))
    if terms:
        logger.debug(f"got terms: '{terms}'")
    else:
        logger.debug("Got no terms")
        terms = list()
    # exit()
    cs_prefix = escape(unquote(request.args.get("prefix", "")))
    if cs_prefix:
        logger.debug(f"got cirrussearch string: '{cs_prefix}'")
    cs_affix = escape(unquote(request.args.get("affix", "")))
    if cs_affix:
        logger.debug(f"got cirrussearch affix: '{cs_affix}'")
    try:
        if limit_param:
            limit = int(limit_param)
        else:
            # Default to 10
            limit = 10
    except ValueError:
        return jsonify(error="Limit must be an integer."), 400
    topic = TopicItem(qid=qid)
    if not topic.is_valid:
        logger.debug(f"Invalid qid {topic.model_dump()}")
        return jsonify(invalid_format)
    if topic.label is None or not topic.label:
        return jsonify(f"topic label was empty, please go add an english label in Wikidata. See {topic.url}")
    # Call the GetArticles function with the provided variables
    articles = Articles(
        parameters=Parameters(
            topic=topic,
            limit=limit,
            cirrussearch=Cirrussearch(
                prefix=cs_prefix, affix=cs_affix, topic=topic, search_terms=terms
            ),
            search_terms=terms,
        )
    )
    # Run the queries
    articles.get_items()
    return render_template(
        ["results.html"],
        queries=articles.get_query_html_rows(),
        item_count=articles.item_count,
        article_rows=articles.get_item_html_rows(),
        qid=qid,
        label=articles.parameters.topic.label,
        link=topic.url,
    )


def generate_qs_commands(main_subject: str, selected_qids: List[str]):
    commands = list()
    for qid in selected_qids:
        #  based on heuristic -> inferred from title
        commands.append(f"{qid}|P921|{main_subject}|S887|Q69652283")
    return "||".join(commands)


@app.route("/add-main-subject", methods=["POST"])
def add_main_subject():
    if request.method == "POST":
        selected_qids = [escape(qid) for qid in request.form.getlist("selected_qids[]")]
        topic = escape(request.form.get("main_subject"))
        if selected_qids and topic:
            if len(selected_qids) > 30 and os.environ.get('USER') is None:
                # Toolforge does not have USER set
                return jsonify("Error: Toolforge does not support long URLs "
                               "so we cannot process this many QIDs at once. "
                               "An OAUTH rewrite is planned, see "
                               "https://github.com/dpriskorn/WikidataTopicCurator/issues/5")
            # Handle the selected_qids as needed
            print(f"Got topic: {topic}")
            print("Selected QIDs:", selected_qids)
            commands = generate_qs_commands(
                main_subject=topic, selected_qids=selected_qids
            )
            # https://quickstatements.toolforge.org/#/v1=%7CCREATE%7C%7C%7CLAST%7CP31%7CQ13442814%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CLen%7C%22Empirical%20research%20on%20parental%20alienation%3A%20A%20descriptive%20literature%20review%22%7C%7C%7CLAST%7CP304%7C%22105572%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP356%7C%2210.1016%2FJ.CHILDYOUTH.2020.105572%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP407%7CQ1860%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP478%7C%22119%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP577%7C%2B2020-12-01T00%3A00%3A00Z%2F10%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP1433%7CQ15753235%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP1476%7Cen%3A%22Empirical%20research%20on%20parental%20alienation%3A%20A%20descriptive%20literature%20review%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22T.M.%20Marques%22%7CP1545%7C%221%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22I.%20Narciso%22%7CP1545%7C%222%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22L.C.%20Ferreira%22%7CP1545%7C%223%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C
            base_url = "https://quickstatements.toolforge.org"
            endpoint = f"{base_url}/#/v1="
            url = f"{endpoint}{quote(commands)}"
            print(f"url to qs: {url}")
            return redirect(location=url, code=302)
        return jsonify(f"Error: No QIDs selected.")


if __name__ == "__main__":
    app.run(debug=True)
