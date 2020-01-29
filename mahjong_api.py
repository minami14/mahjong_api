import flask
from mahjong.constants import EAST, NORTH, SOUTH, WEST
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/win", methods=["POST"])
def win():
    req = flask.request.get_json()
    calculator = HandCalculator()

    try:
        tiles = TilesConverter.one_line_string_to_136_array(req["hands"], has_aka_dora=True)
    except KeyError:
        return flask.jsonify({"error": "hands required"}), 400
    except ValueError:
        return flask.jsonify({"error": "invalid hands"}), 400

    try:
        win_tile = TilesConverter.one_line_string_to_136_array(req["win_tile"], has_aka_dora=True)[0]
    except KeyError:
        return flask.jsonify({"error": "win_tile required"}), 400
    except ValueError:
        return flask.jsonify({"error": "invalid win_tile"}), 400

    melds = []
    try:
        melds = req["melds"]
    except KeyError:
        pass

    meld_tiles = []
    for meld in melds:
        try:
            m = meld["meld"]
        except KeyError:
            return flask.jsonify({"error": "meld required"}), 400
        try:
            if m == "chi":
                meld_tiles.append(Meld(Meld.CHI, TilesConverter.one_line_string_to_136_array(meld["tiles"])))
            elif m == "pon":
                meld_tiles.append(Meld(Meld.PON, TilesConverter.one_line_string_to_136_array(meld["tiles"])))
            elif m == "minkan":
                meld_tiles.append(Meld(Meld.KAN, TilesConverter.one_line_string_to_136_array(meld["tiles"]), True))
            elif m == "ankan":
                meld_tiles.append(Meld(Meld.KAN, TilesConverter.one_line_string_to_136_array(meld["tiles"]), False))
            elif m == "kakan":
                meld_tiles.append(Meld(Meld.CHANKAN, TilesConverter.one_line_string_to_136_array(meld["tiles"])))
            else:
                return flask.jsonify({"error": "invalid meld"}), 400
        except KeyError:
            return flask.jsonify({"error": "meld tiles required"}), 400
        except ValueError:
            return flask.jsonify({"error": "invalid meld tiles"}), 400

    try:
        tsumo = req["tsumo"]
    except KeyError:
        tsumo = False

    try:
        riichi = req["riichi"]
    except KeyError:
        riichi = False

    try:
        ippatsu = req["ippatsu"]
    except KeyError:
        ippatsu = False

    try:
        rinshan = req["rinshan"]
    except KeyError:
        rinshan = False

    try:
        chankan = req["chankan"]
    except KeyError:
        chankan = False

    try:
        haitei = req["haitei"]
    except KeyError:
        haitei = False

    try:
        houtei = req["houtei"]
    except KeyError:
        houtei = False

    try:
        double_riichi = req["double_riichi"]
    except KeyError:
        double_riichi = False

    try:
        tenhou = req["tenhou"]
    except KeyError:
        tenhou = False

    try:
        chiihou = req["chiihou"]
    except KeyError:
        chiihou = False

    try:
        wind_player = req["wind_player"]
        if wind_player == "east":
            wind_player = EAST
        elif wind_player == "south":
            wind_player = SOUTH
        elif wind_player == "west":
            wind_player = WEST
        elif wind_player == "north":
            wind_player = NORTH
        else:
            return flask.jsonify({"error": "invalid wind_player"}), 400
    except KeyError:
        return flask.jsonify({"error": "wind_player required"}), 400

    try:
        wind_round = req["wind_round"]
        if wind_round == "east":
            wind_round = EAST
        elif wind_round == "south":
            wind_round = SOUTH
        elif wind_round == "west":
            wind_round = WEST
        elif wind_round == "north":
            wind_round = NORTH
        else:
            return flask.jsonify({"error": "invalid wind_round"}), 400
    except KeyError:
        return flask.jsonify({"error": "wind_round required"}), 400

    try:
        dora_indicators = TilesConverter.one_line_string_to_136_array(req["dora_indicators"], has_aka_dora=True)
    except KeyError:
        return flask.jsonify({"error": "dora_indicators required"}), 400
    except ValueError:
        return flask.jsonify({"error": "invalid dora_indicators"}), 400

    option = OptionalRules(has_open_tanyao=True,
                           has_aka_dora=True,
                           has_double_yakuman=False)

    config = HandConfig(is_tsumo=tsumo,
                        is_riichi=riichi,
                        is_ippatsu=ippatsu,
                        is_rinshan=rinshan,
                        is_chankan=chankan,
                        is_haitei=haitei,
                        is_houtei=houtei,
                        is_daburu_riichi=double_riichi,
                        is_tenhou=tenhou,
                        is_chiihou=chiihou,
                        player_wind=wind_player,
                        round_wind=wind_round,
                        options=option)

    result = calculator.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators, config=config)

    if result.error:
        return flask.jsonify({"error": result.error}), 400

    yaku = map(lambda y: y.japanese, result.yaku)
    return flask.jsonify({"cost": result.cost, "han": result.han, "fu": result.fu, "yaku": list(yaku), "error": None})
    

@app.route("/shanten", methods=["POST"])
def shanten():
    shanten = Shanten()
    req = flask.request.get_json()

    try:
        tiles = TilesConverter.one_line_string_to_34_array(req["hands"])
    except KeyError:
        return flask.jsonify({"error": "hands required"}), 400

    result = shanten.calculate_shanten(tiles)

    if result == -2:
        return flask.jsonify({"error": "hands over 14 tiles"}), 400

    return flask.jsonify({"shanten": result, "error": None})


if __name__ == "__main__":
    app.run()
