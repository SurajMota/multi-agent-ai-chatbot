import os

# Define folder structure
folders = [
    "backend/app/agents",
    "backend/app/core",
    "backend/app/memory",
    "backend/app/tools",
    "backend/app/routes",
    "backend/app/services",
    "backend/server/schemas",
    "frontend/public",
    "frontend/src/components",
    "frontend/src/hooks",
    "frontend/src/utils",
    "frontend/src/styles",
    "frontend/src/config",
    "widget",
    "knowledgebase/pdfs",
    "knowledgebase/text",
    "knowledgebase/embeddings"
]

# Define empty files to generate
files = [
    "backend/app/agents/base_agent.py",
    "backend/app/agents/general_agent.py",
    "backend/app/agents/appointment_agent.py",
    "backend/app/agents/update_agent.py",
    "backend/app/agents/rag_agent.py",
    "backend/app/agents/sentiment_agent.py",
    "backend/app/core/llm_provider.py",
    "backend/app/core/rag.py",
    "backend/app/core/embeddings.py",
    "backend/app/core/cache.py",
    "backend/app/memory/memory_store.py",
    "backend/app/tools/extractors.py",
    "backend/app/tools/formatters.py",
    "backend/app/tools/logger.py",
    "backend/app/routes/chat_routes.py",
    "backend/app/routes/admin_routes.py",
    "backend/app/services/sheet_writer.py",
    "backend/app/services/pinecone_service.py",
    "backend/app/services/make_webhook.py",
    "backend/app/config.py",
    "backend/app/chat.py",
    "backend/server/main.py",
    "backend/server/utils.py",
    "backend/server/db.py",
    "backend/server/schemas/lead_schema.sql",
    "backend/README.md",
    "backend/requirements.txt",
    "frontend/src/components/ChatBubble.js",
    "frontend/src/components/ChatWindow.js",
    "frontend/src/components/MessageList.js",
    "frontend/src/components/TypingIndicator.js",
    "frontend/src/components/ThemeSwitcher.js",
    "frontend/src/hooks/useChatbot.js",
    "frontend/src/utils/formatMessage.js",
    "frontend/src/styles/chat.css",
    "frontend/src/config/theme.js",
    "frontend/src/App.js",
    "frontend/src/index.js",
    "frontend/public/logo.png",
    "frontend/public/avatar.png",
    "frontend/README.md",
    "frontend/package.json",
    "widget/chatbot.js",
    "widget/styles.css",
    "widget/index.html",
    "knowledgebase/config.json",
    ".env.example",
    "README.md"
]

def create_structure():
    print("Creating full project structure...")

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create empty files
    for file in files:
        with open(file, "w", encoding="utf-8") as f:
            f.write("")  # empty placeholder
        print(f"Created file: {file}")

    print("\n🎉 Project structure created successfully!")


if __name__ == "__main__":
    create_structure()
