def print_story_status(state: StoryState):
    """Print current story status with language support"""
    print(f"📖 STORY STATUS:")
    print(f"   ID: {state.story_id}")
    print(f"   Turn: {state.current_turn}/{state.max_turns}")
    print(f"   Cosmic Position: {state.cosmic_position}")
    print(f"   Language: {state.language}")
    print()