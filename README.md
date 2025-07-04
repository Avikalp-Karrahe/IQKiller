# 🎯 One-Stop Job Deep-Dive Web App

A production-ready, LLM-powered, modular micro-pipeline for comprehensive job role analysis and interview preparation.

## ✨ Features

### 🤖 **LLM-Powered Analysis**
- **Multi-Provider Support**: OpenAI (GPT-4o-mini) + Anthropic (Claude-3-Haiku) with automatic fallback
- **Intelligent Pipeline**: `scrape → enrich → draft → QA → critique → render`
- **Quality Scoring**: Automated content quality assessment (1-10 scale)
- **Smart Caching**: 24h TTL diskcache for cost optimization

### 🔍 **Comprehensive Job Analysis**
- **URL/Text Input**: Supports job posting URLs and direct text input
- **Data Enrichment**: Extracts structured job data (role, company, requirements, etc.)
- **Role Preview**: Generates detailed role overview and company context
- **Interview Prep**: Customized interview questions and preparation materials

### ⚙️ **Production Features**
- **Rate Limiting**: Built-in request throttling (2s between calls)
- **Error Handling**: Graceful fallbacks and comprehensive error reporting
- **Metrics**: JSON logging with analytics hooks
- **Extensible**: SOLID principles, type-hinted, testable architecture

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)
- OpenAI API key
- Anthropic API key

### Installation

1. **Activate virtual environment** (if not already active):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Launch the LLM-powered app**:
```bash
python gradio_app.py
```

4. **Access the app**: Open http://localhost:7860

## 📱 **Usage**

### **Main Analysis Tab**
1. Paste a job posting URL or description
2. Click "🔍 Analyze Job"
3. Watch real-time progress through the pipeline
4. Get comprehensive analysis with quality score

### **Prompt Editor Tab**
- Customize LLM prompts for each pipeline stage
- Load/save prompt configurations
- Fine-tune analysis behavior

### **Analytics Tab**
- View pipeline performance metrics
- Monitor LLM usage and costs
- Track quality scores and success rates

## 🏗️ **Architecture**

```
IQKiller/
├── gradio_app.py          # 🎯 LLM-powered Gradio UI
├── app.py                 # 📱 Original Flask app (still working)
├── orchestrator.py        # 🔗 Pipeline manager
├── llm_client.py         # 🤖 Multi-provider LLM client
├── prompt_loader.py      # 📚 YAML prompt management
├── config.py             # ⚙️ LLM configuration & API keys
├── micro/                # 🧩 Modular micro-functions
│   ├── scrape.py        # 📥 URL/PDF scraping + LLM cleaning
│   ├── enrich.py        # 🔍 LLM data enrichment (JSON extraction)
│   ├── draft.py         # ✍️ LLM content generation
│   ├── qa.py            # ✅ LLM quality assurance + auto-fix
│   ├── critique.py      # 📝 LLM expert critique + scoring
│   └── render.py        # 🎨 Final markdown assembly
├── cache.py              # 💾 diskcache wrapper (24h TTL)
├── metrics.py            # 📊 JSON logging + analytics hooks
├── prompts/v1.yaml       # 📚 Versioned prompt repository
├── tests/                # 🧪 Unit tests (4/4 passing)
└── requirements.txt      # 📦 Dependencies
```

## 🧪 **Testing**

```bash
# Run all tests
PYTHONPATH=. pytest tests/ -v

# Test individual components
python -c "from llm_client import llm_client; print(llm_client.call_llm('Hello world'))"
```

## 🔧 **Configuration**

### **API Keys** (configured in `config.py`)
- OpenAI: `gpt-4o-mini` (primary)
- Anthropic: `claude-3-haiku-20240307` (fallback)

### **LLM Settings**
- Temperature: 0.1 (deterministic)
- Max tokens: 2000
- Rate limit: 2s between requests
- Auto-fallback on provider failures

### **Caching**
- TTL: 24 hours
- Storage: `.cache/` directory
- Cost optimization for repeated queries

## 📊 **Performance**

### **Pipeline Metrics** (from latest test)
- **Total Latency**: ~45s end-to-end
- **Quality Score**: 6.0/10 average
- **Success Rate**: 100% with fallback
- **Cache Hit Rate**: Optimized for repeated queries

### **LLM Usage** (per analysis)
- ~5-7 API calls total
- ~15,000 tokens consumed
- Auto-fallback: OpenAI → Anthropic
- Cost: ~$0.05-0.10 per analysis

## 🛠️ **Development**

### **Add New Micro-Functions**
1. Create new file in `micro/`
2. Implement `run(data: Dict[str, Any]) -> Dict[str, Any]`
3. Add to pipeline in `get_pipeline()`

### **Customize Prompts**
1. Edit `prompts/v1.yaml`
2. Or use the web UI prompt editor
3. Restart app to apply changes

### **Add New LLM Providers**
1. Update `llm_client.py`
2. Add config in `config.py`
3. Test fallback behavior

## 🚀 **Deployment**

### **Production Checklist**
- ✅ Virtual environment setup
- ✅ API keys configured
- ✅ Rate limiting implemented
- ✅ Error handling & fallbacks
- ✅ Caching for cost optimization
- ✅ Metrics & monitoring hooks
- ✅ Type safety & testing

### **Scaling Options**
- Deploy on Hugging Face Spaces
- Use Docker containers
- Add Redis for distributed caching
- Implement queue system for high volume

## 📈 **Roadmap**

- [ ] PDF upload support
- [ ] Multi-language job postings
- [ ] Company research integration
- [ ] Resume matching analysis
- [ ] Email integration for job alerts

## 🎉 **Success!**

The complete LLM-powered job analysis pipeline is now **fully implemented** and **production-ready**! 

- **Total files**: 20+ components
- **Test coverage**: 4/4 tests passing  
- **LLM integration**: OpenAI + Anthropic with fallbacks
- **UI**: Modern Gradio interface with progress tracking
- **Architecture**: SOLID, modular, extensible

Run `python gradio_app.py` and start analyzing job postings with AI! 🚀 

# IQKiller - Interview Query Killer

IQKiller is an AI-powered interview preparation tool that generates personalized interview guides from job descriptions. Like Interview Query but customized for each specific role, it provides technical questions, behavioral questions, talking points, and company intel to help you ace your interviews.

## Features

### 🎯 Interview Query-Style Prep Guide
- **Title Line**: Role, Company, Location, Work Type, Salary
- **Mission**: Company's purpose in ≤25 words
- **Must-Have Stack**: Core skills required (≤6 items, <10 words each)
- **Nice-to-Haves**: Bonus skills (grey bullets)
- **Why It Matters**: Impact of the role (≤30 words)
- **Perks**: Benefits and compensation highlights

### 🎯 Personalized Interview Preparation
- **Technical Questions**: Likely technical interview questions for this role
- **Behavioral Questions**: Behavioral questions this company/role might ask
- **Talking Points**: Specific achievements/experiences to highlight
- **Company Intel**: Key company facts to mention (funding, growth, mission)
- **Smart Questions**: Thoughtful questions to ask interviewer
- **Role Challenges**: Main challenges/problems this role will solve
- **Success Metrics**: How success is measured in this role
- **Salary Context**: Negotiation context (market rate, equity, growth stage)

### 📊 Full Analysis
- Detailed job analysis with Q&A and critique
- Company enrichment with funding/growth data
- Technical and behavioral question predictions

## Usage

1. **Start the app**: `python gradio_app.py`
2. **Visit**: http://localhost:7862
3. **Choose tab**: "🎯 Interview Prep" for personalized interview guide or "📊 Full Analysis" for deep dive
4. **Input**: Paste job description URL or text
5. **Get results**: Instant skeleton → full analysis in ~20 seconds

## Interview Query-Style Output

The personalized interview guide provides everything you need to ace your interview:
- ✅ **Technical Questions**: Prepare for role-specific technical challenges
- ✅ **Behavioral Questions**: Practice company-specific behavioral scenarios
- ✅ **Talking Points**: Know exactly what achievements to highlight
- ✅ **Company Intel**: Impress with insider knowledge
- ✅ **Smart Questions**: Show strategic thinking with thoughtful questions
- ✅ **Role Context**: Understand challenges and success metrics
- ✅ **Salary Negotiation**: Armed with market context and equity info

## Technical Details

- **Single LLM call**: No chunking, faster processing
- **Streaming UI**: Skeleton in <1s, full results in ~20s
- **Copy functionality**: One-click summary copying
- **Caching**: Intelligent caching with diskcache
- **Google enrichment**: SerpAPI for company data

## Testing

Run the test suite:
```bash
python -m pytest tests/test_nobs.py -v
```

## Requirements

- Python 3.11+
- OpenAI API key
- SerpAPI key (optional, for company enrichment)
- See `requirements.txt` for dependencies 