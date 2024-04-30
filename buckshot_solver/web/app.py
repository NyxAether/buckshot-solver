from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug import Response

from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.round import Round
from buckshot_solver.simulator import Simulator

app = Flask(__name__)
app.secret_key = "secret"


@app.route("/")
def index() -> str:
    if "cr" not in session:
        cr = Round(
            lives=1,
            blanks=1,
            max_life=2,
            player_life=2,
            dealer_life=2,
        )
        session["cr"] = cr.model_dump()
    return render_template("base.html")


@app.route("/submit", methods=["POST"])
def submit() -> "Response":
    keys = request.form.keys()
    shell_map = {"L": Shell.live, "B": Shell.blank, "U": Shell.unknown}

    lives = int(request.form["lives"])
    blanks = int(request.form["blanks"])
    player_life = int(request.form["player_life"])
    dealer_life = int(request.form["dealer_life"])
    max_life = int(request.form["max_life"])
    dealer_handcuff = "dealer_handcuff" in request.form
    saw_bonus = 2 if "ac_saw" in request.form else 1
    shells = [shell_map[request.form[k]] for k in keys if "shell_" in k]
    if (lives + blanks) < len(shells):
        shells = shells[: (lives + blanks)]
    elif (lives + blanks) > len(shells):
        shells = [Shell.unknown] * (lives + blanks)
    items_player = [
        Item.from_str(request.form[k].strip()) for k in keys if "item_player_" in k
    ]
    items_dealer = [
        Item.from_str(request.form[k].strip()) for k in keys if "item_dealer_" in k
    ]

    cr = Round(
        lives=lives,
        blanks=blanks,
        max_life=max_life,
        player_life=player_life,
        dealer_life=dealer_life,
        dealer_handcuff=dealer_handcuff,
        saw_bonus=saw_bonus,
        items_player=items_player,
        items_dealer=items_dealer,
        shells=shells.copy(),
        player_shells=shells.copy(),
    )
    res = Simulator(cr).start()
    scores = {Action.int_to_str(k): res[k] for k in res}
    session["cr"] = cr.model_dump()
    print(session["cr"])
    print(request.form)
    session["scores"] = scores
    session["action_max"] = max(scores, key=scores.__getitem__)
    print(scores)
    return redirect(url_for("index"))
