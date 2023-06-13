from html2image import Html2Image
import os

from dbio import get_season_scoreboard

from dotenv import load_dotenv

load_dotenv()

CHROME_EXE = os.getenv("CHROME_EXE")

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
            <th class='yellow'>Date</th>
            <th class='yellow'>Wordle</th>
            <th class='yellow'>Word</th>
            <th class='green'>{"</th><th class='green'>".join([player for player in headers[3:]])}</th>
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
    yellow = '#c8b653'
    green = '#6ca965'
    grey = '#787c7f'
    css = [
        'body { background-color: black }',
        'table { width:100%; border-collapse: separate; border-spacing: 4px; font-size: 14px;  font-weight: bold; font-family: Arial, sans-serif; color: white !important; }', 
        'th, td { text-align: center; vertical-align: middle; padding-top: 5px; padding-bottom: 5px; background-color: black; border-width: 2px; border }',
        f'.yellow {{background-color: {yellow}}}',
        f'.green {{background-color: {green}}}'
        ]

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
    hti = Html2Image(custom_flags=['--no-sandbox'], browser_executable=CHROME_EXE) 
    # Need --no-sandbox to run in docker container
    
    html, css = get_scoreboard_html_and_css(database, season_id)

    path = hti.screenshot(html_str=html, css_str=css, save_as='scoreboard.png', size=(800, 1200))[0]

    return path
