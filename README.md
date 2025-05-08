#folktale generator

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run the application
python api.py

# Start a bilingual story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "both"}'

# Start a Chinese-only story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "zh"}'

# Start an English-only story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Switch language of active story
curl -X POST http://localhost:5555/language/both
curl -X POST http://localhost:5555/language/zh
curl -X POST http://localhost:5555/language/en

# Continue story (language is saved in the story state)
curl -X POST http://localhost:5555/next_turn

# Get a list of all available story arc types
curl http://localhost:5555/story_arcs

# Start a classic "quest" story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "both", "arc_type": "quest"}'

# Generate a bureaucratic trial story (underworld judgment)
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "zh", "arc_type": "bureaucratic_trial"}'