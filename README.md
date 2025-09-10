# 🏈 Fantasy Football AI Commissioner

An intelligent fantasy football assistant that generates creative weekly recaps and summaries using AI. Transform your league's weekly performance data into entertaining, character-driven narratives that bring your fantasy football experience to life.

## ✨ Features

### 🤖 AI-Powered Summaries
- **Multiple OpenAI Models**: Choose from GPT-4o, GPT-4o Mini, GPT-5, O3, O3 Mini, and more
- **Real-time Cost Tracking**: See exact token usage and costs for each summary
- **Character Personas**: Generate summaries in the style of John Madden, Dwight Schrute, or any character you choose
- **Customizable Trash Talk**: Adjustable intensity from friendly banter to hardcore roasting

### 🏆 League Integration
- **ESPN Fantasy**: Full integration with ESPN fantasy football leagues
- **Sleeper**: Complete support for Sleeper fantasy leagues
- **Yahoo Fantasy**: Backend support (UI removed for streamlined experience)

### 🔒 Security & Authentication
- **Password Protection**: Secure access with 24-hour session persistence
- **Streamlit Secrets**: Secure credential management
- **Session Management**: Automatic logout after 24 hours

### 📊 Advanced Analytics
- **Weekly Performance Analysis**: Highest/lowest scorers, biggest blowouts, closest matches
- **Player Insights**: Best bench players, worst starters, injury reports
- **Team Statistics**: Transaction tracking, standings, and more
- **Cost Optimization**: Model recommendations for best creativity-to-cost ratio

### 🏆 Statistical Power Rankings
- **Objective Team Analysis**: Data-driven power rankings separate from AI summaries
- **Multiple Ranking Algorithms**: Comprehensive score, Oberon Mt. Power Rating, Team Value Index
- **Dual Display Formats**: Choose between detailed list view or compact table view
- **Performance Metrics**: Win percentage, scoring averages, consistency, recent form analysis
- **Sleeper Integration**: Full support for Sleeper fantasy leagues

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit account (for deployment)
- OpenAI API key
- Fantasy league credentials (ESPN or Sleeper)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JoshFink/commish.git
   cd commish
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets**
   Create `.streamlit/secrets.toml`:
   ```toml
   [default]
   APP_PASSWORD = "your_secure_password_here"
   OPENAI_ORG_ID = "your_openai_org_id"
   OPENAI_API_PROJECT_ID = "your_project_id"
   OPENAI_COMMISH_API_KEY = "your_api_key"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

1. **Access the App**: Enter your password to authenticate
2. **Select League Type**: Choose ESPN or Sleeper from the dropdown
3. **Enter League Details**: 
   - **ESPN**: League ID, SWID, and ESPN_S2 tokens
   - **Sleeper**: League ID only
4. **Customize Your Summary**:
   - Character Description (default: John Madden)
   - Trash Talk Level (1-10 scale)
   - OpenAI Model Selection
5. **Generate**: Click "🤖 Generate AI Summary" and watch your recap come to life!
6. **Power Rankings**: Use "📊 Calculate Power Rankings" for objective statistical analysis

## 🎭 Character Examples

- **John Madden**: Classic football commentary with "BOOM!" and telestrator enthusiasm
- **Dwight Schrute**: Beet farm analogies and intense competitive analysis
- **Captain Jack Sparrow**: Pirate-themed adventure narratives about your league
- **Gordon Ramsay**: Brutal honesty with British profanity about team performance
- **Tony Stark**: Sarcastic genius billionaire analysis with tech references
- **Shaquille O'Neal**: Big personality commentary with playful roasting and nicknames
- **Charles Barkley**: Unfiltered opinions and hilarious hot takes about your league
- **Ryan Reynolds**: Witty fourth-wall-breaking commentary with self-deprecating humor
- **Samuel L. Jackson**: Intense, memorable quotes with that unmistakable attitude
- **Snoop Dogg**: Laid-back, cool commentary with unique vocabulary and style
- **Stone Cold Steve Austin**: WWE-style trash talk with "And that's the bottom line!"
- **Morgan Freeman**: Dignified, profound narration that makes fantasy football epic
- **Deadpool**: Breaking the fourth wall with irreverent humor and pop culture refs
- **Joe Rogan**: Deep dive analysis with random tangents and "Have you ever tried..."
- **Stephen A. Smith**: LOUD, passionate takes with "HOWEVER!" and dramatic proclamations
- **Weird Al Yankovic**: Parody song lyrics turned into fantasy football commentary
- **Custom Characters**: Describe any persona for unique summaries

## 📊 Power Rankings System

Transform your league's statistical data into comprehensive power rankings that go beyond simple win-loss records.

### 🏆 Ranking Algorithms

**Comprehensive Power Score (Primary)**
- 30% Win Percentage (managerial skill)
- 25% Scoring Average (offensive production) 
- 20% Point Differential (dominance)
- 15% Recent Form (momentum)
- 10% Consistency (reliability)

**Oberon Mt. Power Rating**
- 60% Average Score + 20% High/Low Score Average + 20% Win Percentage
- Balanced approach emphasizing consistent scoring with win rate consideration
- Goal: Higher scores indicate better overall team strength

**Team Value Index** 
- (Points For / Points Against) × Win Percentage
- Measures efficiency by combining scoring differential with actual wins achieved
- Goal: Higher values show you're winning games efficiently relative to points

### 📋 Display Options

**📋 List View**
- Detailed text-based rankings with full explanations
- Complete methodology breakdown
- All alternative ranking methods included
- Perfect for comprehensive analysis

**📊 Table View** 
- Compact, responsive table format
- Optimized column widths for maximum data visibility
- Collapsible methodology section
- Dynamic height based on league size
- Side-by-side alternative rankings comparison

### 🎯 Current Support
- **Sleeper Leagues**: Full integration with comprehensive data analysis
- **ESPN/Yahoo**: Coming soon

## 💰 Cost Management

| Model | Input Cost | Output Cost | Best For |
|-------|------------|-------------|----------|
| GPT-4o Mini | $0.15/1M | $0.60/1M | ⭐ Recommended balance |
| GPT-4o | $2.50/1M | $10.00/1M | 🎭 Maximum creativity |
| GPT-5 | $1.25/1M | $10.00/1M | 🆕 Latest technology |
| O3 | $2.00/1M | $8.00/1M | 🧠 Advanced reasoning |

## 🔧 Configuration

### ESPN Setup
1. Find your League ID in your ESPN league URL
2. Get SWID and ESPN_S2 using the [Chrome extension](https://chrome.google.com/webstore/detail/espn-private-league-key-a/bakealnpgdijapoiibbgdbogehhmaopn)
3. Alternatively, follow [manual steps](https://www.gamedaybot.com/help/espn_s2-and-swid/)

### Sleeper Setup
1. Find your League ID in your Sleeper app or [follow this guide](https://support.sleeper.com/en/articles/4121798-how-do-i-find-my-league-id)

### OpenAI Setup
1. Create an account at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key in your dashboard
3. Add your organization and project IDs for better tracking

## 🏗️ Architecture

```
commish/
├── app.py                      # Main Streamlit application
├── utils/
│   ├── summary_generator.py     # OpenAI integration and streaming
│   ├── power_ranking_generator.py # Statistical power rankings system
│   ├── model_config.py         # Model pricing and recommendations
│   ├── espn_helper.py          # ESPN API utilities
│   ├── sleeper_helper.py       # Sleeper API utilities
│   ├── yahoo_helper.py         # Yahoo API utilities (legacy)
│   └── helper.py               # General utilities
├── requirements.txt           # Python dependencies
└── AUTHENTICATION_SETUP.md    # Detailed auth configuration
```

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your secrets in the app settings
4. Deploy with one click!

### Local Development
```bash
streamlit run app.py --server.port 8501
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

- `streamlit==1.49.1` - Web application framework
- `openai==1.107.0` - OpenAI API client
- `espn-api==0.45.1` - ESPN fantasy API
- `sleeper-api-wrapper==1.1.0` - Sleeper fantasy API
- `yfpy==16.0.3` - Yahoo fantasy API
- `pytz==2025.2` - Timezone handling
- `httpx==0.28.1` - HTTP client for OpenAI
- `reportlab==4.2.2` - PDF generation for summaries
- `pandas>=2.0.0` - Data manipulation for power rankings

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/JoshFink/commish/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/JoshFink/commish/discussions)
- 📖 **Documentation**: Check `AUTHENTICATION_SETUP.md` for detailed setup

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the amazing web framework
- Powered by [OpenAI](https://openai.com/) for intelligent content generation
- Fantasy APIs: ESPN, Sleeper, and Yahoo for league data access
- Community contributors for feature requests and bug reports

---

<div align="center">
  <p><strong>Made with ❤️ for fantasy football commissioners everywhere</strong></p>
  <p>Transform your league's data into entertainment • One recap at a time</p>
</div>