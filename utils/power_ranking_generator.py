"""
Power Rankings Generator for Fantasy Football Leagues

This module calculates objective power rankings based on multiple statistical metrics:
- Wins and Win Percentage (managerial skill)
- Points Scored (offensive production)
- Points Against (defensive luck/strength of schedule)
- Recent Performance Trends
- Scoring Consistency (high/low analysis)
- Point Differential Analysis

Supports multiple ranking formulas including Oberon Mt. Power Rating style calculations.
"""

from sleeper_wrapper import League as SleeperLeague
from utils import sleeper_helper, helper
import datetime
import statistics
from typing import List, Dict, Tuple, Any


class PowerRankingCalculator:
    """Calculate comprehensive power rankings for fantasy football teams."""
    
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.league = SleeperLeague(league_id)
        self.current_week = helper.get_current_week(datetime.datetime.now()) - 1
        self.team_data = {}
        self.league_averages = {}
        
    def gather_team_data(self) -> Dict[str, Any]:
        """Collect all necessary data for power ranking calculations."""
        
        # Get basic league data
        rosters = self.league.get_rosters()
        users = self.league.get_users()
        standings = self.league.get_standings(rosters, users)
        
        # Create mappings
        user_team_mapping = self.league.map_users_to_team_name(users)
        roster_owner_mapping = self.league.map_rosterid_to_ownerid(rosters)
        
        # Initialize team data structure
        for roster in rosters:
            owner_id = roster['owner_id']
            team_name = user_team_mapping.get(owner_id, f"Team {roster['roster_id']}")
            
            self.team_data[team_name] = {
                'roster_id': roster['roster_id'],
                'owner_id': owner_id,
                'weekly_scores': [],
                'wins': 0,
                'losses': 0,
                'points_for': 0,
                'points_against': 0,
                'recent_form': [],  # Last 3 weeks
                'highest_score': 0,
                'lowest_score': float('inf'),
                'win_streak': 0,
                'loss_streak': 0
            }
        
        # Collect weekly data
        for week in range(1, self.current_week + 1):
            try:
                matchups = self.league.get_matchups(week)
                scoreboards = sleeper_helper.calculate_scoreboards(matchups, user_team_mapping, roster_owner_mapping)
                
                # Process each matchup
                for matchup_id, teams in scoreboards.items():
                    if len(teams) == 2:
                        winner = teams[0]  # teams are sorted by points descending
                        loser = teams[1]
                        
                        # Update winner stats
                        winner_name = winner[0]
                        winner_score = winner[1]
                        if winner_name in self.team_data:
                            self.team_data[winner_name]['weekly_scores'].append(winner_score)
                            self.team_data[winner_name]['wins'] += 1
                            self.team_data[winner_name]['points_for'] += winner_score
                            self.team_data[winner_name]['points_against'] += loser[1]
                            self.team_data[winner_name]['highest_score'] = max(
                                self.team_data[winner_name]['highest_score'], winner_score
                            )
                            self.team_data[winner_name]['lowest_score'] = min(
                                self.team_data[winner_name]['lowest_score'], winner_score
                            )
                            
                            # Recent form (last 3 weeks)
                            if week > self.current_week - 3:
                                self.team_data[winner_name]['recent_form'].append('W')
                        
                        # Update loser stats
                        loser_name = loser[0]
                        loser_score = loser[1]
                        if loser_name in self.team_data:
                            self.team_data[loser_name]['weekly_scores'].append(loser_score)
                            self.team_data[loser_name]['losses'] += 1
                            self.team_data[loser_name]['points_for'] += loser_score
                            self.team_data[loser_name]['points_against'] += winner_score
                            self.team_data[loser_name]['highest_score'] = max(
                                self.team_data[loser_name]['highest_score'], loser_score
                            )
                            self.team_data[loser_name]['lowest_score'] = min(
                                self.team_data[loser_name]['lowest_score'], loser_score
                            )
                            
                            # Recent form (last 3 weeks)
                            if week > self.current_week - 3:
                                self.team_data[loser_name]['recent_form'].append('L')
                                
            except Exception as e:
                print(f"Error processing week {week}: {e}")
                continue
        
        # Calculate derived metrics
        for team_name in self.team_data:
            data = self.team_data[team_name]
            games_played = data['wins'] + data['losses']
            
            if games_played > 0:
                data['win_percentage'] = data['wins'] / games_played
                data['avg_points_for'] = data['points_for'] / games_played
                data['avg_points_against'] = data['points_against'] / games_played
                data['point_differential'] = data['points_for'] - data['points_against']
                data['avg_point_differential'] = data['point_differential'] / games_played
                
                # Scoring consistency (standard deviation)
                if len(data['weekly_scores']) > 1:
                    data['score_std_dev'] = statistics.stdev(data['weekly_scores'])
                    data['consistency_score'] = 1 / (1 + data['score_std_dev'])  # Higher = more consistent
                else:
                    data['score_std_dev'] = 0
                    data['consistency_score'] = 1
                
                # Recent form score (last 3 games)
                recent_wins = data['recent_form'].count('W')
                recent_games = len(data['recent_form'])
                data['recent_form_pct'] = recent_wins / recent_games if recent_games > 0 else 0
                
                # Fix infinite lowest score
                if data['lowest_score'] == float('inf'):
                    data['lowest_score'] = 0
            else:
                # Default values for teams with no games
                data['win_percentage'] = 0
                data['avg_points_for'] = 0
                data['avg_points_against'] = 0
                data['point_differential'] = 0
                data['avg_point_differential'] = 0
                data['score_std_dev'] = 0
                data['consistency_score'] = 0
                data['recent_form_pct'] = 0
                data['lowest_score'] = 0
        
        return self.team_data
    
    def calculate_league_averages(self):
        """Calculate league-wide averages for normalization."""
        if not self.team_data:
            return
        
        teams_with_games = [data for data in self.team_data.values() if data['wins'] + data['losses'] > 0]
        
        if teams_with_games:
            self.league_averages = {
                'avg_points_for': statistics.mean([team['avg_points_for'] for team in teams_with_games]),
                'avg_points_against': statistics.mean([team['avg_points_against'] for team in teams_with_games]),
                'avg_win_pct': statistics.mean([team['win_percentage'] for team in teams_with_games]),
                'avg_point_diff': statistics.mean([team['avg_point_differential'] for team in teams_with_games])
            }
    
    def oberon_power_rating(self, team_data: Dict) -> float:
        """
        Calculate Oberon Mt. Power Rating style formula:
        60% Average Score + 20% (High + Low)/2 + 20% Win Percentage, divided by 10
        """
        avg_score_component = team_data['avg_points_for'] * 0.6
        high_low_component = ((team_data['highest_score'] + team_data['lowest_score']) / 2) * 0.2
        win_pct_component = (team_data['win_percentage'] * 100) * 0.2
        
        return (avg_score_component + high_low_component + win_pct_component) / 10
    
    def team_value_index(self, team_data: Dict) -> float:
        """
        Calculate Team Value Index: (Avg Points For / Avg Points Against) * Win %
        """
        if team_data['avg_points_against'] == 0:
            return 0
        
        return (team_data['avg_points_for'] / team_data['avg_points_against']) * team_data['win_percentage']
    
    def comprehensive_power_score(self, team_data: Dict) -> float:
        """
        Calculate a comprehensive power score combining multiple factors:
        - 30% Win Percentage
        - 25% Average Points For (normalized)
        - 20% Point Differential (normalized)
        - 15% Recent Form
        - 10% Consistency
        """
        if not self.league_averages:
            return 0
        
        # Normalize components
        win_pct_norm = team_data['win_percentage']
        
        # Points for normalized against league average
        points_for_norm = team_data['avg_points_for'] / self.league_averages['avg_points_for'] if self.league_averages['avg_points_for'] > 0 else 0
        
        # Point differential normalized
        point_diff_norm = (team_data['avg_point_differential'] - self.league_averages['avg_point_diff']) / 10  # Scale down
        point_diff_norm = max(min(point_diff_norm, 1), -1)  # Cap between -1 and 1
        point_diff_norm = (point_diff_norm + 1) / 2  # Convert to 0-1 scale
        
        # Recent form (already 0-1)
        recent_form_norm = team_data['recent_form_pct']
        
        # Consistency (already 0-1)
        consistency_norm = team_data['consistency_score']
        
        # Weighted combination
        power_score = (
            win_pct_norm * 0.30 +
            points_for_norm * 0.25 +
            point_diff_norm * 0.20 +
            recent_form_norm * 0.15 +
            consistency_norm * 0.10
        )
        
        return power_score
    
    def generate_power_rankings(self) -> List[Dict[str, Any]]:
        """Generate comprehensive power rankings with multiple ranking methods."""
        
        # Gather all team data
        self.gather_team_data()
        self.calculate_league_averages()
        
        # Calculate rankings for each team
        rankings = []
        for team_name, data in self.team_data.items():
            team_ranking = {
                'team_name': team_name,
                'record': f"{data['wins']}-{data['losses']}",
                'win_percentage': data['win_percentage'],
                'points_for': data['points_for'],
                'points_against': data['points_against'],
                'avg_points_for': data['avg_points_for'],
                'avg_points_against': data['avg_points_against'],
                'point_differential': data['point_differential'],
                'avg_point_differential': data['avg_point_differential'],
                'highest_score': data['highest_score'],
                'lowest_score': data['lowest_score'],
                'consistency_score': data['consistency_score'],
                'recent_form': ''.join(data['recent_form'][-3:]) if data['recent_form'] else 'N/A',
                'recent_form_pct': data['recent_form_pct'],
                
                # Power Rating Calculations
                'oberon_rating': self.oberon_power_rating(data),
                'team_value_index': self.team_value_index(data),
                'comprehensive_score': self.comprehensive_power_score(data)
            }
            rankings.append(team_ranking)
        
        # Sort by comprehensive power score (highest first)
        rankings.sort(key=lambda x: x['comprehensive_score'], reverse=True)
        
        # Add rank numbers
        for i, team in enumerate(rankings):
            team['power_rank'] = i + 1
        
        return rankings


def get_sleeper_power_rankings_data(league_id: str) -> Dict[str, Any]:
    """
    Get raw power rankings data for a Sleeper league.
    
    Args:
        league_id: Sleeper league ID
    
    Returns:
        Dictionary containing rankings data and metadata
    """
    try:
        calculator = PowerRankingCalculator(league_id)
        rankings = calculator.generate_power_rankings()
        
        if not rankings:
            return {"error": "Unable to generate power rankings - insufficient data."}
        
        return {
            "rankings": rankings,
            "current_week": calculator.current_week,
            "league_averages": calculator.league_averages
        }
        
    except Exception as e:
        return {"error": f"Error generating power rankings: {str(e)}"}


def generate_sleeper_power_rankings(league_id: str) -> str:
    """
    Generate formatted power rankings for a Sleeper league.
    
    Args:
        league_id: Sleeper league ID
    
    Returns:
        Formatted string containing power rankings and analysis
    """
    try:
        calculator = PowerRankingCalculator(league_id)
        rankings = calculator.generate_power_rankings()
        
        if not rankings:
            return "Unable to generate power rankings - insufficient data."
        
        # Format the output
        current_week = calculator.current_week
        output = []
        output.append(f"🏆 POWER RANKINGS - AFTER WEEK {current_week}")
        output.append("=" * 60)
        output.append("")
        
        # Rankings table
        for team in rankings:
            output.append(f"#{team['power_rank']} {team['team_name']} ({team['record']})")
            output.append(f"   📊 Power Score: {team['comprehensive_score']:.3f}")
            output.append(f"   📈 Avg Points: {team['avg_points_for']:.1f} | Point Diff: {team['avg_point_differential']:+.1f}")
            output.append(f"   🎯 Win %: {team['win_percentage']:.1%} | Recent: {team['recent_form']} ({team['recent_form_pct']:.1%})")
            output.append(f"   🏅 High: {team['highest_score']:.1f} | Low: {team['lowest_score']:.1f}")
            output.append("")
        
        # Additional metrics
        output.append("📋 RANKING METHODOLOGY:")
        output.append("Power Score Breakdown:")
        output.append("• 30% Win Percentage (managerial skill)")
        output.append("• 25% Scoring Average (offensive production)")  
        output.append("• 20% Point Differential (dominance)")
        output.append("• 15% Recent Form (momentum)")
        output.append("• 10% Consistency (reliability)")
        output.append("")
        
        # Alternative rankings
        output.append("🔬 ALTERNATIVE RANKINGS:")
        output.append("")
        
        # Oberon Method
        oberon_rankings = sorted(rankings, key=lambda x: x['oberon_rating'], reverse=True)
        output.append("Oberon Mt. Power Rating (60% Avg Score, 20% High/Low, 20% Win %):")
        for i, team in enumerate(oberon_rankings[:5]):
            output.append(f"  {i+1}. {team['team_name']}: {team['oberon_rating']:.2f}")
        output.append("")
        
        # Team Value Index
        tvi_rankings = sorted(rankings, key=lambda x: x['team_value_index'], reverse=True)
        output.append("Team Value Index (Points For/Against * Win %):")
        for i, team in enumerate(tvi_rankings[:5]):
            output.append(f"  {i+1}. {team['team_name']}: {team['team_value_index']:.3f}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error generating power rankings: {str(e)}"


if __name__ == "__main__":
    # Test with a sample league ID
    sample_league_id = "your_league_id_here"
    result = generate_sleeper_power_rankings(sample_league_id)
    print(result)