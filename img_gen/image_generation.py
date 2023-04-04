from html2image import Html2Image

from dbio import get_season_scoreboard

def get_total_scores(data):
    # Returns player scores in a list
    no_players = len(data[0][3:])
    sums = [0] * no_players

    for wordle_day in data:
        for player_index in range(no_players):
            sums[player_index] += wordle_day[3:][player_index]

    return sums

def get_scoreboard_html_and_css(database, season_id):

    data, headers = get_season_scoreboard(database, season_id) 


    html = f"""
<html>
    <body>

    <table border="1" align="center" >
    <thead>
        <tr>
            <th>{headers[0]}</th>
            <th>{headers[1]}</th>
            <th>{headers[2]}</th>
            <th>{"</th><th>".join([player for player in headers[3:]])}</th>
        </tr>

        <tr>
            <th colspan="3">TOTALS</th>
            <th>{"</th><th>".join(str(score) for score in get_total_scores(data))}
        </tr>

    </thead>
    <tfoot>
    </tfoot>
    <tbody>

        <tr>{"</tr><tr>".join(f"<td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{'</td><td>'.join(str(score) for score in row[3:])}</th>" for row in data)}</td>

        <!--
        Nicely formatted sample of what the monstrosity above generates:
        <tr>
            <td>2023-03-12</td>
            <td>SMART</td>
            <td >566</td>
            <td >4</td>
            <td >7</td>
            <td >6</td>
        </tr>
        <tr>
            <td>2023-03-13</td>
            <td>DUMPS</td>
            <td>567</td>
            <td>6</td>
            <td>7</td>
            <td>3</td>
        </tr>-->
    </tbody>
</table>
</body>
</html>
    """
    css = ['body {background:red;}','table {width:100%}', 'td {text-align: center;}', 'tr {height:30px}']

    return (html, css)


def generate_scoreboard_image(database, season_id):
    """
    Generate the PNG image of the wordle scoreboard

    Parameters
    ----------
    season_id: int
        Unique season identifier

    Returns
    -------
    String
        Returns a list containing the path to the scoreboard image that was generated

    Raises
    ------
    None

    Notes
    -----
    None
    """
    hti = Html2Image()
    
    html, css = get_scoreboard_html_and_css(database, season_id)

    return hti.screenshot(html_str=html, css_str=css, save_as='scoreboard.png', size=(800, 1050))[0]
