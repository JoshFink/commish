from espn_api.football import League
from yfpy.query import YahooFantasySportsQuery
from sleeper_wrapper import League as SleeperLeague
from utils import espn_helper, yahoo_helper, sleeper_helper, helper
# from openai import OpenAI
from openai import OpenAI
import datetime
import os
import streamlit as st
from streamlit.logger import get_logger
LOGGER = get_logger(__name__)

def moderate_text(client, text):
    try:
        # Send the moderation request
        response = client.moderations.create(
            input=text,
            model="text-moderation-latest"  # Use the latest moderation model
        )
        
        # Extract the first result
        result = response.results[0]
        
        # Check if the content is flagged
        if result.flagged:
            # Log the flagged categories
            flagged_categories = [category for category, flagged in result.categories.items() if flagged]
            print(f"Moderation flagged the following categories: {', '.join(flagged_categories)}")
            return False  # Return False if any category is flagged
        return True  # Content is not flagged, return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False  # Assume text is inappropriate in case of an error

# Lateny troubleshooting: https://platform.openai.com/docs/guides/production-best-practices/improving-latencies

def generate_gpt4_summary_streaming(client, summary, character_choice, trash_talk_level, model="gpt-4o-mini", summary_format="Classic"):
    # Construct the instruction for GPT-4 based on user inputs and format choice
    if summary_format == "Detailed":
        instruction = f"""You will be provided a summary below containing the most recent weekly stats for a fantasy football league.

Create an EPIC, comprehensive, and hilariously detailed weekly recap in the style of {character_choice}. This should be a masterpiece of fantasy football commentary - think ESPN highlight reel meets roast comedy special. Make it LONG, DETAILED, FUNNY, and SNARKY.

STRUCTURE YOUR RECAP AS FOLLOWS:

1. **DRAMATIC WEEK OPENING** (2-3 paragraphs): 
   - Start with a theatrical introduction about the week's chaos
   - Set the scene like you're narrating a sports documentary
   - Mention the biggest storylines, upsets, and drama
   - Use vivid metaphors and colorful language

2. **LEAGUE POWER RANKINGS ROAST** (1-2 paragraphs):
   - Discuss current standings with BRUTAL honesty
   - Mock the pretenders, praise the contenders
   - Make predictions and throw shade at playoff hopes
   - Be SNARKY about team management decisions

3. **MATCHUP-BY-MATCHUP DESTRUCTION** (This is the MAIN EVENT - be thorough):
   For EVERY SINGLE matchup, provide:
   - A creative nickname/storyline for each game ("The Bloodbath," "David vs Goliath," etc.)
   - Detailed play-by-play style commentary on what happened
   - ROAST poor performances mercilessly (within trash talk level {trash_talk_level})
   - Celebrate great performances with over-the-top praise
   - Make jokes about team names, player choices, and strategies
   - Include specific point totals and what they mean
   - Create dramatic narratives around close games and blowouts
   - Don't just report scores - tell the STORY of each battle

4. **HEROES AND VILLAINS OF THE WEEK** (2-3 paragraphs):
   - Crown the week's MVP with fanfare
   - Publicly shame the biggest busts and disappointments  
   - Highlight clutch performances and epic failures
   - Make it personal and hilarious

5. **THE WEEKLY AWARDS CEREMONY**:
   - "Manager of the Week" (with sarcastic reasoning)
   - "Worst Decision Award" (roast bad start/sit choices)
   - "Luckiest SOB Award" 
   - "Most Disappointing Roster Award"
   - Be creative with categories and RUTHLESS with commentary

6. **TRASH TALK AND PREDICTIONS**:
   - Unleash appropriate trash talk (level {trash_talk_level}/10)
   - Make bold predictions for next week
   - Call out managers by name for their successes/failures
   - End with a memorable one-liner or challenge

WRITING STYLE REQUIREMENTS:
- Write 1500-2500 words minimum - make it SUBSTANTIAL
- Channel {character_choice} personality throughout
- Use humor, sarcasm, and wit liberally
- Include sports analogies and pop culture references
- Be entertaining AF - this should be the highlight of their week
- Make managers want to share this with everyone
- Don't just list stats - weave them into compelling narratives
- Be detailed enough that someone who didn't watch can visualize everything

REMEMBER: This isn't just a summary - it's ENTERTAINMENT. Make it legendary.

Here is the provided weekly fantasy summary: {summary}"""
    else:
        # Classic format (existing)
        instruction = f"""You will be provided a summary below containing the most recent weekly stats for a fantasy football league.

Create a hilarious and engaging weekly recap in the style of {character_choice}. This should be substantially longer, funnier, and more detailed than a typical summary.

YOUR MISSION:
- Write 800-1200 words of pure entertainment
- Channel {character_choice}'s personality with humor and wit
- Include trash talk at level {trash_talk_level}/10 (be appropriately ruthless)
- Make this the most anticipated part of their league experience

CONTENT REQUIREMENTS:
- Start with a memorable character introduction
- Cover ALL the major storylines and matchups from the week  
- Roast poor performances and celebrate great ones
- Make jokes about team names, player choices, and league drama
- Include specific stats but weave them into funny narratives
- Add sports analogies, pop culture references, and witty observations
- Create memorable one-liners and quotable moments
- End with trash talk and predictions for next week

STYLE GUIDELINES:
- Be SNARKY and HILARIOUS while staying true to {character_choice}
- Don't just report stats - tell entertaining stories about what happened
- Make fun of bad decisions and praise smart moves
- Create dramatic tension around close games and mock blowouts
- Use vivid descriptions and colorful language
- Include thematic emojis that enhance the humor
- Make every manager want to keep reading until the end

REMEMBER: You're not just summarizing - you're ENTERTAINING. Make this recap so good that managers screenshot it and share it with friends. This should be comedy gold that brings the league together through laughter (and friendly roasting).

Here is the provided weekly fantasy summary: {summary}"""

    # Create the messages array
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    try:
        # Send the messages to OpenAI for analysis with selected model
        response = client.chat.completions.create(
            model=model,  # Use the selected model
            messages=messages,
            max_tokens=15000,  # Control response length
            stream=True,
            stream_options={"include_usage": True}  # Enable usage tracking for cost calculation
        )
        
        # Extract and yield the generated message, capturing usage data
        usage_data = None
        content_chunks = []
        
        for chunk in response:
            # Debug: Log chunk structure
            LOGGER.debug(f"Chunk type: {type(chunk)}, has usage: {hasattr(chunk, 'usage')}")
            
            # Check if this chunk contains usage information (final chunk)
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                usage_data = chunk.usage
                LOGGER.debug(f"Usage data found: {usage_data}")
            
            # Process content chunks
            if chunk.choices and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_chunks.append(content)
                yield content
        
        # After streaming is complete, yield usage data if available
        if usage_data:
            LOGGER.debug(f"Yielding usage data: prompt={usage_data.prompt_tokens}, completion={usage_data.completion_tokens}, total={usage_data.total_tokens}")
            yield f"__USAGE_DATA__{usage_data.prompt_tokens},{usage_data.completion_tokens},{usage_data.total_tokens}__{model}__"
        else:
            # Fallback: If no usage data captured, log this for debugging
            LOGGER.warning("No usage data captured from streaming response")
            # Try to estimate tokens as fallback
            total_content = ''.join(content_chunks)
            estimated_output_tokens = len(total_content) // 4  # Rough estimate
            LOGGER.debug(f"Fallback: estimated output tokens: {estimated_output_tokens}")
            yield f"__USAGE_DATA_FALLBACK__{estimated_output_tokens}__{model}__"

    except Exception as e:
        error_str = str(e)
        # Handle specific OpenAI API errors with user-friendly messages
        if "insufficient_quota" in error_str or "429" in error_str:
            yield "⚠️ OpenAI API quota exceeded. Please check your billing plan or try again later."
        elif "401" in error_str or "unauthorized" in error_str.lower():
            yield "🔐 OpenAI API key is invalid or expired. Please check your credentials."
        elif "503" in error_str or "service_unavailable" in error_str:
            yield "🔧 OpenAI service is temporarily unavailable. Please try again in a few minutes."
        elif "rate_limit" in error_str.lower() or "too_many_requests" in error_str.lower():
            yield "⏱️ Rate limit exceeded. Please wait a moment and try again."
        else:
            # Generic error message for other issues
            yield f"❌ Unable to generate AI summary. Please try again later. (Error: {type(e).__name__})"

# @st.cache_data(ttl=3600) - Cannot hash argument 'league'
def generate_espn_summary(league, cw):
    """
    Generate a human-friendly summary based on the league stats.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - str: A human-friendly summary.
    """
    # Extracting required data using helper functions
    start_time = datetime.datetime.now()
    top_teams = espn_helper.top_three_teams(league)
    print(f"Time for top_three_teams: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scorer_week = espn_helper.top_scorer_of_week(league, cw)
    print(f"Time for top_scorer_of_week: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    worst_scorer_week = espn_helper.worst_scorer_of_week(league, cw)
    print(f"Time for worst_scorer_of_week: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scorer_szn = espn_helper.top_scorer_of_season(league)
    print(f"Time for top_scorer_of_season: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    worst_scorer_szn = espn_helper.worst_scorer_of_season(league)
    print(f"Time for worst_scorer_of_season: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    most_trans = espn_helper.team_with_most_transactions(league)
    print(f"Time for team_with_most_transactions: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    most_injured = espn_helper.team_with_most_injured_players(league)
    print(f"Time for team_with_most_injured_players: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    highest_bench = espn_helper.highest_scoring_benched_player(league, cw)
    print(f"Time for highest_scoring_benched_player: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    lowest_start = espn_helper.lowest_scoring_starting_player(league, cw)
    print(f"Time for lowest_scoring_starting_player: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    biggest_blowout = espn_helper.biggest_blowout_match(league, cw)
    print(f"Time for biggest_blowout_match: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    closest_game = espn_helper.closest_game_match(league, cw)
    print(f"Time for closest_game_match: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scoring_team_Week = espn_helper.highest_scoring_team(league, cw)
    print(f"Time for top_scoring_team_string: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    # Formatting the summary
    summary = f"""
    - Top scoring fantasy team this week: {top_scoring_team_Week} 
    - Top 3 fantasy teams: {espn_helper.clean_team_name(top_teams[0].team_name)}, {espn_helper.clean_team_name(top_teams[1].team_name)}, {espn_helper.clean_team_name(top_teams[2].team_name)}
    - Top scoring NFL player of the week: {top_scorer_week[0].name} with {top_scorer_week[1]} points.
    - Worst scoring NFL player of the week: {worst_scorer_week[0].name} with {worst_scorer_week[1]} points.
    - Top scoring NFL player of the season: {top_scorer_szn[0].name} with {top_scorer_szn[1]} points.
    - Worst scoring NFL player of the season: {worst_scorer_szn[0].name} with {worst_scorer_szn[1]} points.
    - Fantasy Team with the most transactions: {espn_helper.clean_team_name(most_trans[0].team_name)} ({most_trans[1]} transactions)
    - Fantasy Team with the most injured players: {espn_helper.clean_team_name(most_injured[0].team_name)} ({most_injured[1]} players: {', '.join(most_injured[2])})
    - Highest scoring benched player: {highest_bench[0].name} with {highest_bench[0].points} points (Rostered by {espn_helper.clean_team_name(highest_bench[1].team_name)})
    - Lowest scoring starting player of the week: {lowest_start[0].name} with {lowest_start[0].points} points (Rostered by {espn_helper.clean_team_name(lowest_start[1].team_name)})
    - Biggest blowout match of the week: {espn_helper.clean_team_name(biggest_blowout.home_team.team_name)} ({biggest_blowout.home_score} points) vs {espn_helper.clean_team_name(biggest_blowout.away_team.team_name)} ({biggest_blowout.away_score} points)
    - Closest game of the week: {espn_helper.clean_team_name(closest_game.home_team.team_name)} ({closest_game.home_score} points) vs {espn_helper.clean_team_name(closest_game.away_team.team_name)} ({closest_game.away_score} points)
    """
    
    return summary.strip()

@st.cache_data(ttl=3600)
def get_espn_league_summary(league_id, espn2, SWID):
    # Fetch data from ESPN Fantasy API and compute statistics   
    start_time_league_connect = datetime.datetime.now() 
    league_id = league_id
    year = datetime.datetime.now().year
    espn_s2 = espn2
    swid = SWID
    # Initialize league & current week
    try:
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    except Exception as e:
        return str(e), "Error occurred during validation"
    end_time_league_connect = datetime.datetime.now()
    league_connect_duration = (end_time_league_connect - start_time_league_connect).total_seconds()
    cw = league.current_week-1
    # Generate summary
    start_time_summary = datetime.datetime.now()
    summary = generate_espn_summary(league, cw)
    end_time_summary = datetime.datetime.now()
    summary_duration = (end_time_summary - start_time_summary).total_seconds()
    # Generage debugging information, placeholder for now
    debug_info = "Summary: " + summary + " ~~~Timings~~~ " + f"League Connect Duration: {league_connect_duration} seconds " + f"Summary Duration: {summary_duration} seconds "
    return summary, debug_info

@st.cache_data(ttl=3600)
def get_yahoo_league_summary(league_id, auth_path):    
    league_id = league_id
    LOGGER.info(f"League id: {league_id}")
    auth_directory = auth_path
    sc = YahooFantasySportsQuery(
        auth_dir=auth_directory,
        league_id=league_id,
        game_code="nfl"
    )
    LOGGER.info(f"sc: {sc}")
    mrw = yahoo_helper.get_most_recent_week(sc)
    recap = yahoo_helper.generate_weekly_recap(sc, week=mrw)
    return recap


@st.cache_data(ttl=3600)
def generate_sleeper_summary(league_id):
    # Initialize the Sleeper API League object
    league = SleeperLeague(league_id)
    current_date_today = datetime.datetime.now()
    week = helper.get_current_week(current_date_today)-1 #force to always be most recent completed week
    # Get necessary data from the league
    rosters = league.get_rosters()
    users = league.get_users()
    matchups = league.get_matchups(week)
    standings = league.get_standings(rosters, users)

    # Get weekly players data from public json file
    players_url = "https://raw.githubusercontent.com/jeisey/commish/main/players_data.json"
    players_data = sleeper_helper.load_player_data(players_url)

    # Generate mappings
    user_team_mapping = league.map_users_to_team_name(users)
    roster_owner_mapping = league.map_rosterid_to_ownerid(rosters)
    
    # Generate scoreboards for the week
    scoreboards = sleeper_helper.calculate_scoreboards(matchups, user_team_mapping, roster_owner_mapping)

    # 1. Highest Scoring Team of the Week
    highest_scoring_team_name, highest_scoring_team_score = sleeper_helper.highest_scoring_team_of_week(scoreboards)

    # 2. Standings; Top 3 Teams
    top_3_teams_result = sleeper_helper.top_3_teams(standings)
    
    # 3. Highest Scoring Player of the Week
    highest_scoring_player_week, weekly_score, highest_scoring_player_team_week = sleeper_helper.highest_scoring_player_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping)

    # 4. Lowest Scoring Player of the Week that Started
    lowest_scoring_starter, lowest_starter_score, lowest_scoring_starter_team = sleeper_helper.lowest_scoring_starter_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping)

    # 5. Highest Scoring Benched Player of the Week
    highest_scoring_benched_player, highest_benched_score, highest_scoring_benched_player_team = sleeper_helper.highest_scoring_benched_player_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping)

    # 6. Biggest Blowout Match of the Week
    blowout_teams, point_differential_blowout = sleeper_helper.biggest_blowout_match_of_week(scoreboards)

    # 7. Closest Match of the Week
    close_teams, point_differential_close = sleeper_helper.closest_match_of_week(scoreboards)

    # 8. Team with Most Moves (this always seems to be zero, UPDATE)
    # team_most_moves, most_moves = sleeper_helper.team_with_most_moves(rosters, user_team_mapping, roster_owner_mapping)
    
    # 9. Team on Hottest Streak
    hottest_streak_team, longest_streak = sleeper_helper.team_on_hottest_streak(rosters, user_team_mapping, roster_owner_mapping)
    
    # 10. All Individual Matchups
    matchup_details = ""
    # Sort matchups by ID to display in order (1-6)
    for matchup_id in sorted(scoreboards.keys()):
        teams = scoreboards[matchup_id]
        if len(teams) == 2:
            winner = teams[0]  # teams are sorted by points descending
            loser = teams[1]
            point_diff = round(winner[1] - loser[1], 2)
            matchup_details += f"• Matchup {matchup_id}: {winner[0]} ({round(winner[1], 2)}) defeated {loser[0]} ({round(loser[1], 2)}) by {point_diff} points\n"

    # Construct the summary string with proper formatting and line breaks
    summary = (
        f"🏆 WEEK {week} FANTASY RECAP\n"
        f"{'='*50}\n\n"
        
        f"⭐ TOP PERFORMER\n"
        f"{highest_scoring_team_name} with {round(highest_scoring_team_score,2)} points\n\n"
        
        f"📊 LEAGUE STANDINGS - TOP 3\n"
        f"🥇 {top_3_teams_result[0][0]} - {top_3_teams_result[0][3]} points ({top_3_teams_result[0][1]}W-{top_3_teams_result[0][2]}L)\n"
        f"🥈 {top_3_teams_result[1][0]} - {top_3_teams_result[1][3]} points ({top_3_teams_result[1][1]}W-{top_3_teams_result[1][2]}L)\n"
        f"🥉 {top_3_teams_result[2][0]} - {top_3_teams_result[2][3]} points ({top_3_teams_result[2][1]}W-{top_3_teams_result[2][2]}L)\n\n"
        
        f"🌟 PLAYER HIGHLIGHTS\n"
        f"• Best Player: {highest_scoring_player_week} with {weekly_score} points (Team: {highest_scoring_player_team_week})\n"
        f"• Worst Starter: {lowest_scoring_starter} with {lowest_starter_score} points (Team: {lowest_scoring_starter_team})\n"
        f"• Best Benched: {highest_scoring_benched_player} with {highest_benched_score} points (Team: {highest_scoring_benched_player_team})\n\n"
        
        f"🏈 ALL MATCHUPS - WEEK {week}\n"
        f"{matchup_details}\n"
        
        f"📈 WEEK STATS\n"
        f"💥 Biggest Blowout: {blowout_teams[0]} vs {blowout_teams[1]} (Point Differential: {round(point_differential_blowout, 2)})\n"
        f"⚡ Closest Match: {close_teams[0]} vs {close_teams[1]} (Point Differential: {round(point_differential_close, 2)})\n"
        f"🔥 Hottest Streak: {hottest_streak_team} with a {longest_streak} game win streak\n"
    )
    LOGGER.info(f"Sleeper Summary Generated: \n{summary}")

    return summary
