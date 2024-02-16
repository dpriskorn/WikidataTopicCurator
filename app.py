import logging
import os
from urllib.parse import quote, unquote

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from markupsafe import Markup, escape

from models.enums import Source, Subgraph
from models.results import Results
from models.term import Term
from models.terms import Terms
from models.topic_item import TopicItem
from models.topicparameters import TopicParameters

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

invalid_format = "Not a valid QID, format must be 'Q[0-9]+'"
# generated using toolforge.set_user_agent(
#     "topic-curator",
#     url="https://github.com/dpriskorn/WikidataTopicCurator/",
#     email="User:So9q",
# )
user_agent = "topic-curator (https://github.com/dpriskorn/WikidataTopicCurator/; User:So9q) python-requests/2.31.0"
default_limit = 8000
documentation_url = (
    "https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Topic_Curator"
)

# # Setup database config
# db_config = LoadDatabaseConfig()
# db_config.load_config()
# app.config["SQLALCHEMY_DATABASE_URI"] = db_config.get_db_uri
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)
#
#
# @app.route("/store_batch", methods=["GET"])
# def store_batch():
#     """Store batches sent to QuickStatements
#
#     This enables us to show statistics in the first page
#     and encourage people to finish matching of topics
#     (or re-run the matching if more than a year has passed)"""
#     qid = escape(request.args.get("qid"))
#     lang = escape(request.args.get("lang", ""))
#     prefix = escape(request.args.get("prefix"))
#     affix = escape(request.args.get("affix"))
#     count = escape(request.args.get("count"))
#     to_be_matched = escape(request.args.get("to_be_matched"))
#
#     # Check if all required parameters are provided
#     # affix can be None
#     if (
#         qid is None
#         or count is None
#         or to_be_matched is None
#         or prefix is None
#         or lang is None
#     ):
#         error_response = {
#             "error": "The parameters (qid, count, to_be_matched, prefix, lang) are required."
#         }
#         return jsonify(error_response), 400  # 400 Bad Request status code
#
#     # Convert qid and count to integers
#     try:
#         count = int(count)
#         to_be_matched = int(to_be_matched)
#     except ValueError:
#         error_response = {"error": "qid and count must be integers."}
#         return jsonify(error_response), 400
#     if qid:
#         topic = TopicItem(qid=qid, lang=lang)
#         if not topic.is_valid:
#             return jsonify(error=invalid_format), 400
#
#     # Attempt to store the batch information in the database
#     try:
#         from models.database.batch import Batch
#
#         new_batch = Batch(
#             qid=qid,
#             count=count,
#             to_be_matched=to_be_matched,
#             affix=affix,
#             prefix=prefix,
#             lang=lang,
#         )
#         db.session.add(new_batch)
#         db.session.commit()
#     except Exception as e:
#         error_response = {"error": f"Error storing batch information: {str(e)}"}
#         return jsonify(error_response), 500  # 500 Internal Server Error status code
#
#     # Return a success message
#     success_response = {"message": "Batch information stored successfully."}
#     return jsonify(success_response)
#
#
# @app.route("/mark-as-finished", methods=["GET"])
# def mark_as_finished():
#     """Store qids as finished
#
#     This enables us to show statistics
#     in the first page by username
#     and suggest re-run of the matching
#     if more than a year has passed)"""
#     qid = escape(request.args.get("qid"))
#     username = escape(request.args.get("username"))
#
#     if qid is None or username is None:
#         error_response = {"error": 'Both "qid" and "username" parameters are required.'}
#         return jsonify(error_response), 400  # 400 Bad Request status code
#
#     try:
#         qid = int(qid)
#     except ValueError:
#         return jsonify(error="qid must be an integer."), 400
#
#     # Check if the entry already exists in the finished table
#     from models.database.finished_item import FinishedItem
#
#     existing_entry = FinishedItem.query.filter_by(qid=qid, username=username).first()
#     if existing_entry:
#         return jsonify(error="Entry already marked as finished."), 400
#
#     if qid:
#         topic = TopicItem(qid=qid, lang=lang)
#         if not topic.is_valid:
#             return jsonify(error=invalid_format), 400
#
#     # Store the finished item in the database
#     try:
#         new_finished_item = FinishedItem(qid=qid, username=username)
#         db.session.add(new_finished_item)
#         db.session.commit()
#
#         result = {
#             "message": "QID marked as finished successfully.",
#             "qid": qid,
#             "username": username,
#         }
#
#         return jsonify(result)
#
#     except Exception as e:
#         db.session.rollback()  # Rollback in case of an error
#         error_message = f"Error storing finished item: {str(e)}"
#         return (
#             jsonify(error=error_message),
#             500,
#         )  # 500 Internal Server Error status code


@app.route("/", methods=["GET"])
def index() -> ResponseReturnValue:  # dead:disable
    subgraph = str(escape(request.args.get("subgraph", "")))
    lang = str(escape(request.args.get("lang", "")))
    qid = str(escape(request.args.get("qid", "")))
    if not lang:
        lang = "en"
    return render_template("index.html", qid=qid, lang=lang, subgraph=subgraph)


@app.route("/subgraph", methods=["GET"])
def subgraph() -> ResponseReturnValue:
    lang = escape(request.args.get("lang", ""))
    qid = escape(request.args.get("qid", ""))
    if not qid:
        return jsonify("Error: Got no QID")
    else:
        topic = TopicItem(qid=qid, lang=lang)
        if not topic.is_valid:
            return jsonify(error=invalid_format), 400
        else:
            return render_template("subgraph.html", qid=qid, lang=lang)


@app.route("/check_subclass_of", methods=["GET"])
def check_subclass_of() -> ResponseReturnValue:  # dead:disable
    """This is used to nudge the user to match the subclass of-items first if not already done.

    Upon completion of matching of all the subclass of items, the user can proceede"""
    raw_subgraph = str(escape(request.args.get("subgraph", "")))
    lang = str(escape(request.args.get("lang", "")))
    qid = str(escape(request.args.get("qid", "")))
    if not lang:
        lang = "en"
    if not raw_subgraph:
        # default subgraph
        subgraph = Subgraph.SCIENTIFIC_ARTICLES
    else:
        try:
            subgraph = Subgraph(raw_subgraph)
            logger.debug(f"successfully parsed {subgraph.value}")
        except ValueError:
            return jsonify(
                f"Error: Invalid subgraph '{raw_subgraph}', "
                f"see {documentation_url} for documentation"
            )
    if not qid:
        return jsonify("Error: Got no QID")
    else:
        topic = TopicItem(qid=qid, lang=lang)
        if not topic.is_valid:
            return jsonify(error=invalid_format), 400
        else:
            logger.debug("getting subclass of")
            subtopics = topic.get_subtopics_as_topic_items
            logger.debug(f"got subtopics: {subtopics}")
            subtopics_html_list = []
            for subtopic in subtopics:
                subtopics_html_list.append(subtopic.row_html(subgraph=subgraph))
            subtopic_html = "\n".join(subtopics_html_list)
            return render_template(
                "subclass_of.html",
                label=topic.label,
                qid=qid,
                lang=lang,
                subgraph=subgraph.value,
                subtopic_html=subtopic_html,
            )


@app.route("/term", methods=["GET"])
def term() -> ResponseReturnValue:
    """We either get a get request or a post request
    If we get arguments, prefill the template

    If a given QID has any P279 statement we redirect to /check_subclass_of"""
    lang = escape(request.args.get("lang", ""))
    subgraph = escape(request.args.get("subgraph", ""))
    qid = escape(request.args.get("qid", ""))
    limit = escape(request.args.get("limit", default_limit))
    cs = escape(request.args.get("cs", ""))
    csa = escape(request.args.get("csa", ""))
    raw_terms = request.args.getlist("terms")
    subclass_of_matched = request.args.get("subclass_of_matched", "").lower() == "true"
    logger.debug(f"subclass_of_matched: {subclass_of_matched}")
    if not qid:
        return jsonify("Error: Got no QID")
    else:
        if raw_terms:
            terms = [Term(string=term, source=Source.USER) for term in raw_terms]
            user_terms = Terms(search_terms=set(terms))
            user_terms.prepare()
        else:
            user_terms = Terms()
        topic = TopicItem(qid=qid, lang=lang)
        if not topic.is_valid:
            return jsonify(error=invalid_format), 400
        else:
            logger.debug("got valid qid, checking subclass of")
            has_subclass_of = True
            if not subclass_of_matched:
                subtopics = topic.get_subtopics_as_topic_items
                # pprint(subtopics)
                if subtopics:
                    logger.debug("we found subtopics. redirecting")
                    # see https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments
                    return redirect(
                        url_for(
                            "check_subclass_of", qid=qid, lang=lang, subgraph=subgraph
                        ),
                        302,
                    )
                else:
                    has_subclass_of = False
            if subclass_of_matched or not has_subclass_of:
                logger.debug(
                    "Found no subclass of this topic or the user says they are already matched"
                )
                return render_template(
                    "term.html",
                    label=topic.label,
                    qid=qid,
                    limit=limit,
                    cs=cs,
                    csa=csa,
                    terms_html=user_terms.get_terms_html(topic=topic),
                    subgraph=subgraph,
                    lang=lang,
                    default_limit=default_limit,
                )
            else:
                raise NotImplementedError("this should never be reached")


@app.route("/results", methods=["GET"])
def results() -> ResponseReturnValue:  # noqa: C901, PLR0911, PLR0912
    # TODO too complex, move checking of parameters to a separate function
    qid = escape(request.args.get("qid", ""))
    if not qid:
        return jsonify("Error: Got no QID")
    lang = escape(request.args.get("lang", ""))
    if not lang:
        return jsonify("Error: No language code specified.")
    else:
        if len(lang) > 3:
            return jsonify(
                "Error: The language code is more than 3 chars which not valid."
            )
    limit_param = escape(request.args.get("limit", default_limit))
    raw_subgraph = escape(request.args.get("subgraph", ""))
    if not raw_subgraph:
        # default subgraph
        subgraph = Subgraph.SCIENTIFIC_ARTICLES
    else:
        try:
            subgraph = Subgraph(raw_subgraph)
            logger.debug(f"successfully parsed {subgraph.value}")
        except ValueError:
            return jsonify(
                f"Error: Invalid subgraph '{raw_subgraph}', "
                f"see {documentation_url} for documentation"
            )
    # Handle terms
    raw_terms = request.args.getlist("terms")
    terms = Terms(
        search_terms={
            Term(string=raw_term, source=Source.USER) for raw_term in raw_terms
        }
    )
    terms.prepare()
    cs_prefix = escape(unquote(request.args.get("prefix", "")))
    if cs_prefix:
        logger.debug(f"got cirrussearch string: '{cs_prefix}'")
    cs_affix = escape(unquote(request.args.get("affix", "")))
    if cs_affix:
        logger.debug(f"got cirrussearch affix: '{cs_affix}'")
    if limit_param:
        try:
            limit = int(limit_param)
        except ValueError:
            return jsonify(error="Limit must be an integer."), 400
    else:
        # Default to 50
        limit = default_limit
    topic = TopicItem(qid=qid, lang=lang)
    if not topic.is_valid:
        logger.debug(f"Invalid qid {topic.model_dump()}")
        return jsonify(invalid_format)
    if topic.label is None or not topic.label:
        # avoid hardcoding english here
        return jsonify(
            f"topic label was empty, please go add an "
            f"english label in Wikidata. See {topic.url}"
        )
    # Call the GetArticles function with the provided variables
    results = Results(
        parameters=TopicParameters(
            topic=topic,
            limit=limit,
            user_prefix=cs_prefix,
            affix=cs_affix,
            subgraph=subgraph,
            terms=terms,
        ),
        lang=lang,
    )
    # Run the queries
    results.get_items()
    # todo propagate all parameters so we can increase
    #  the limit with a single click
    return render_template(
        ["results.html"],
        queries=results.get_query_html_rows(),
        item_count=results.number_of_deduplicated_items,
        article_rows=results.get_item_html_rows(),
        qid=qid,
        label=results.parameters.topic.label,
        link=topic.url,
        lang=lang,
        subgraph=subgraph.value,
    )


def generate_qs_commands(main_subject: str, selected_qids: list[Markup]):
    commands = []
    for qid in selected_qids:
        #  based on heuristic -> inferred from title
        commands.append(f"{qid}|P921|{main_subject}|S887|Q69652283")
    return "||".join(commands)


@app.route("/add-main-subject", methods=["POST"])
def add_main_subject() -> ResponseReturnValue:  # dead:disable
    if request.method == "POST":
        selected_qids = [escape(qid) for qid in request.form.getlist("selected_qids[]")]
        topic = escape(request.form.get("main_subject"))
        if selected_qids and topic:
            # Disabled warning, as suggested here https://phabricator.wikimedia.org/T356195
            # if len(selected_qids) > 30 and os.environ.get("USER") is None:
            #     # Toolforge does not have USER set
            #     return jsonify(
            #         "Error: Toolforge does not support long URLs "
            #         "so we cannot process this many QIDs at once. "
            #         "An OAUTH rewrite is planned, see "
            #         "https://github.com/dpriskorn/WikidataTopicCurator/issues/5"
            #     )
            # Handle the selected_qids as needed
            print(f"Got topic: {topic}")
            print(f"Number of items: {len(selected_qids)}")
            logger.debug(f"Selected QIDs: {selected_qids}")
            commands = generate_qs_commands(
                main_subject=topic, selected_qids=selected_qids
            )
            # https://quickstatements.toolforge.org/#/v1=%7CCREATE%7C%7C%7CLAST%7CP31%7CQ13442814%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CLen%7C%22Empirical%20research%20on%20parental%20alienation%3A%20A%20descriptive%20literature%20review%22%7C%7C%7CLAST%7CP304%7C%22105572%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP356%7C%2210.1016%2FJ.CHILDYOUTH.2020.105572%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP407%7CQ1860%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP478%7C%22119%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP577%7C%2B2020-12-01T00%3A00%3A00Z%2F10%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP1433%7CQ15753235%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP1476%7Cen%3A%22Empirical%20research%20on%20parental%20alienation%3A%20A%20descriptive%20literature%20review%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22T.M.%20Marques%22%7CP1545%7C%221%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22I.%20Narciso%22%7CP1545%7C%222%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C%7CLAST%7CP2093%7C%22L.C.%20Ferreira%22%7CP1545%7C%223%22%7CS248%7CQ5188229%7CS813%7C%2B2024-01-23T00%3A00%3A00Z%2F11%7C%7C
            base_url = "https://quickstatements.toolforge.org"
            endpoint = f"{base_url}/#/v1="
            url = f"{endpoint}{quote(string=commands, safe='/|')}"
            print(f"url to qs: {url}")
            return redirect(location=url, code=302)
        return jsonify("Error: No QIDs selected.")
    else:
        return jsonify("Error: Got no POST request")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
