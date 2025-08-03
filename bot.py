"""
Telegram PDF Summarizer Bot - SUMMARY
=======================================================

A user-friendly Telegram bot that summarizes PDF documents using AI.

Author: Abhay Singh | Claue 4.0 Sonnet Thinking 
Dependencies: python-telegram-bot, langchain, langchain-google-genai, pypdf, python-dotenv
"""

import os
import logging
import asyncio
import re
from typing import Optional, Dict
from pathlib import Path

# Environment and configuration
from dotenv import load_dotenv

# Telegram bot imports
from telegram import Update, Document, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

# LangChain imports for document processing and AI integration
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging and monitoring
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states for prompt setting
WAITING_FOR_PROMPT = 1

class PDFSummarizerBot:
    """
    Simple and reliable PDF Summarizer Bot with summary preservation.
    """
    
    def __init__(self):
        """Initialize the bot with API credentials, AI model setup, and user prompt storage."""
        # Load API credentials from environment variables
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Validate that required credentials are present
        if not self.telegram_token or not self.google_api_key:
            raise ValueError("Missing required API keys. Check your .env file.")
        
        # Initialize the Gemini AI model through LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.google_api_key,
            temperature=0.3  # Lower temperature for more focused summaries
        )
        
        # Configure text splitter for large documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,      # Size of each text chunk
            chunk_overlap=200,    # Overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Create downloads directory for temporary PDF storage
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Store user-specific custom prompts (user_id -> custom_prompt)
        self.user_prompts: Dict[int, str] = {}
        
        # Default prompt template
        self.default_prompt = """
Please provide a comprehensive yet concise summary of the following text.
Focus on the main ideas, key points, and important conclusions.
Make the summary informative and well-structured.

Text to summarize:
{text}

SUMMARY:
"""
        
        logger.info("PDFSummarizerBot initialized successfully")

    def escape_markdown_v2(self, text: str) -> str:
        """
        Properly escape special characters for MarkdownV2.
        """
        # Characters that need to be escaped in MarkdownV2
        special_chars = r'_*[]()~`>#+-=|{}.!'
        
        escaped_text = ""
        for char in text:
            if char in special_chars:
                escaped_text += f'\\{char}'
            else:
                escaped_text += char
        
        return escaped_text

    def truncate_message(self, message: str, max_length: int = 4000) -> str:
        """Truncate message if it exceeds Telegram's limits."""
        if len(message) <= max_length:
            return message
        
        truncated = message[:max_length - 100]
        truncated += "\n\n\\.\\.\\. \\(Summary truncated due to length limits\\)"
        return truncated

    def create_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create simple main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🔧 Custom Prompt", callback_data="set_prompt"),
                InlineKeyboardButton("👀 View Prompt", callback_data="show_prompt")
            ],
            [
                InlineKeyboardButton("🔄 Reset Prompt", callback_data="reset_prompt"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_close_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard with close button for popup messages."""
        keyboard = [[InlineKeyboardButton("✅ Close", callback_data="close_message")]]
        return InlineKeyboardMarkup(keyboard)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command with clear, simple instructions."""
        welcome_message = (
            "🤖 *PDF Summarizer Bot*\n\n"
            "*What I do:*\n"
            "I read your PDF files and create smart summaries using AI\\!\n\n"
            "*How to use me:*\n"
            "1️⃣ Just send me any PDF file \\(up to 20MB\\)\n"
            "2️⃣ Wait a moment while I analyze it\n"
            "3️⃣ Get your summary instantly\\!\n\n"
            "*Ready\\?* Send me a PDF file to start\\!\n\n"
            "*Need options\\?* Use the buttons below:"
        )
        
        keyboard = self.create_main_menu_keyboard()
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
        logger.info(f"Start command sent to user {update.effective_user.id}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
        """Handle button callbacks from inline keyboards - """
        query = update.callback_query
        await query.answer()
        
        # Handle close button
        if query.data == "close_message":
            await query.message.delete()
            return None
        
        if query.data == "set_prompt":
            return await self.set_prompt_via_button(query, context)
        elif query.data == "show_prompt":
            await self.show_prompt_via_button(query, context)
        elif query.data == "reset_prompt":
            await self.reset_prompt_via_button(query, context)
        elif query.data == "help":
            await self.help_via_button(query, context)
        
        return None

    async def set_prompt_via_button(self, query, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle set prompt via button - SENDS NEW MESSAGE."""
        # Answer the callback to remove loading state
        await query.answer("Opening prompt setup...")
        
        prompt_instruction = (
            "✏️ *Custom Prompt Setup*\n\n"
            "*Send me your custom instructions for summarizing PDFs\\.*\n\n"
            "*Examples:*\n"
            "• \"Focus on key financial data and recommendations\"\n"
            "• \"Summarize in bullet points with main conclusions\"\n"
            "• \"Extract technical details and implementation steps\"\n\n"
            "*Just type your instructions and send\\.*\n"
            "*Or type* `/cancel` *to go back\\.*"
        )
        
        # Send NEW message instead of editing existing one
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=prompt_instruction,
            parse_mode='MarkdownV2'
        )
        
        # Store context for prompt setting
        context.user_data['setting_prompt'] = True
        context.user_data['original_query'] = query
        
        return WAITING_FOR_PROMPT

    async def show_prompt_via_button(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show current prompt via button - SENDS NEW MESSAGE."""
        # Answer the callback
        await query.answer("Showing current prompt...")
        
        user_id = query.from_user.id
        
        if user_id in self.user_prompts:
            current_prompt = self.user_prompts[user_id]
            prompt_type = "*Custom Prompt*"
        else:
            current_prompt = self.default_prompt
            prompt_type = "*Default Prompt*"
        
        escaped_prompt = self.escape_markdown_v2(current_prompt[:400])
        if len(current_prompt) > 400:
            escaped_prompt += "\\.\\.\\."
        
        close_keyboard = self.create_close_keyboard()
        
        prompt_message = (
            f"📋 {prompt_type}\n\n"
            f"`{escaped_prompt}`\n\n"
            "*This is your current summarization prompt\\.*"
        )
        
        # Send NEW message instead of editing
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=prompt_message,
            parse_mode='MarkdownV2',
            reply_markup=close_keyboard
        )

    async def reset_prompt_via_button(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Reset prompt via button - SENDS NEW MESSAGE."""
        # Answer the callback
        await query.answer("Resetting prompt...")
        
        user_id = query.from_user.id
        
        if user_id in self.user_prompts:
            del self.user_prompts[user_id]
            message = "✅ *Prompt Reset*\n\nNow using the default summarization prompt\\."
        else:
            message = "ℹ️ *Already Default*\n\nYou're already using the default prompt\\."
        
        close_keyboard = self.create_close_keyboard()
        
        # Send NEW message instead of editing
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            parse_mode='MarkdownV2',
            reply_markup=close_keyboard
        )
        
        logger.info(f"Prompt reset for user {user_id}")

    async def help_via_button(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show help via button - SENDS NEW MESSAGE."""
        # Answer the callback
        await query.answer("Opening help...")
        
        help_message = (
            "📚 *Help \\& Instructions*\n\n"
            "*File Requirements:*\n"
            "• PDF files only\n"
            "• Maximum size: 20MB\n\n"
            "*Available Commands:*\n"
            "• `/start` \\- Show main menu\n"
            "• `/cancel` \\- Cancel current operation\n\n"
            "*How It Works:*\n"
            "1\\. Send your PDF file\n"
            "2\\. Bot processes the document\n"
            "3\\. Receive AI\\-generated summary\n\n"
            "*Button Functions:*\n"
            "• *Custom Prompt* \\- Set personalized instructions\n"
            "• *View Prompt* \\- See current prompt\n"
            "• *Reset Prompt* \\- Back to default\n"
            "• *Help* \\- Show this information"
        )
        
        close_keyboard = self.create_close_keyboard()
        
        # Send NEW message instead of editing
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=help_message,
            parse_mode='MarkdownV2',
            reply_markup=close_keyboard
        )

    async def receive_custom_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the user's custom prompt """
        user_id = update.effective_user.id
        custom_prompt = update.message.text.strip()
        
        # Validate prompt contains {text} placeholder or add it
        if '{text}' not in custom_prompt:
            custom_prompt = f"{custom_prompt}\n\nText: {{text}}"
            
        # Store the custom prompt for this user
        self.user_prompts[user_id] = custom_prompt
        
        # Escape the prompt for display
        escaped_prompt = self.escape_markdown_v2(custom_prompt[:150])
        if len(custom_prompt) > 150:
            escaped_prompt += "\\.\\.\\."
        
        close_keyboard = self.create_close_keyboard()
        
        confirmation_message = (
            "✅ *Custom Prompt Saved\\!*\n\n"
            f"*Your prompt:*\n`{escaped_prompt}`\n\n"
            "*This will be used for all your PDF summaries\\.*\n\n"
            "*Ready to test\\?* Send me a PDF file\\!"
        )
        
        await update.message.reply_text(
            confirmation_message, 
            parse_mode='MarkdownV2',
            reply_markup=close_keyboard
        )
        logger.info(f"Custom prompt set for user {user_id}")
        
        # Clean up context
        context.user_data.clear()
        
        return ConversationHandler.END

    async def cancel_prompt_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the prompt setting process."""
        close_keyboard = self.create_close_keyboard()
        
        await update.message.reply_text(
            "❌ *Cancelled*\n\nYour prompt settings remain unchanged\\.",
            parse_mode='MarkdownV2',
            reply_markup=close_keyboard
        )
        
        # Clean up context
        context.user_data.clear()
        
        return ConversationHandler.END

    async def update_progress(self, message, stage: str, icon: str, details: str = "") -> None:
        """Update progress message with current stage."""
        try:
            progress_text = (
                f"{icon} *{stage}*\n\n"
                f"{details}\n\n"
                "Please wait\\.\\.\\."
            )
            
            await message.edit_text(progress_text, parse_mode='MarkdownV2')
        except Exception as e:
            logger.warning(f"Failed to update progress: {e}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process uploaded documents with progress tracking - PRESERVES SUMMARY."""
        processing_message = None
        try:
            document: Document = update.message.document
            user_id = update.effective_user.id
            
            logger.info(f"Document received from user {user_id}: {document.file_name}")
            
            # Validate file type
            if not document.file_name.lower().endswith('.pdf'):
                await update.message.reply_text(
                    "❌ *Wrong File Type*\n\n"
                    "Please send PDF files only\\.",
                    parse_mode='MarkdownV2'
                )
                return
            
            # Check file size
            if document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text(
                    "❌ *File Too Large*\n\n"
                    "Please send files smaller than 20MB\\.",
                    parse_mode='MarkdownV2'
                )
                return
            
            # Start processing
            processing_message = await update.message.reply_text(
                "🚀 *Processing Started*\n\n"
                "Analyzing your PDF\\.\\.\\.",
                parse_mode='MarkdownV2'
            )
            
            # Download
            await self.update_progress(
                processing_message,
                "Downloading",
                "📥",
                f"Getting `{self.escape_markdown_v2(document.file_name)}`"
            )
            
            file_path = await self._download_pdf(document, user_id)
            
            # Load PDF
            await self.update_progress(
                processing_message,
                "Reading PDF",
                "📄",
                "Extracting text content\\.\\.\\."
            )
            
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                raise Exception("Could not extract text from PDF")
            
            page_count = len(documents)
            logger.info(f"Loaded {page_count} pages from PDF")
            
            # Process
            await self.update_progress(
                processing_message,
                "Processing",
                "⚙️",
                f"Analyzing {page_count} pages\\.\\.\\."
            )
            
            chunks = self.text_splitter.split_documents(documents)
            chunk_count = len(chunks)
            
            # AI Analysis
            prompt_type = "custom" if user_id in self.user_prompts else "default"
            await self.update_progress(
                processing_message,
                "AI Analysis",
                "🤖",
                f"Creating summary with {prompt_type} prompt\\.\\.\\."
            )
            
            summary = await self._process_pdf_with_documents(documents, user_id)
            
            # Finalize
            await self.update_progress(
                processing_message,
                "Almost Done",
                "📝",
                "Preparing your summary\\.\\.\\."
            )
            
            # Clean up
            self._cleanup_file(file_path)
            
            # Prepare final message
            escaped_filename = self.escape_markdown_v2(document.file_name)
            escaped_summary = self.escape_markdown_v2(summary)
            
            response_message = (
                "✅ *Summary Complete\\!*\n\n"
                f"*File:* {escaped_filename}\n"
                f"*Pages:* {page_count} \\- *Chunks:* {chunk_count}\n"
                f"*Prompt:* {prompt_type.title()}\n\n"
                f"*Summary:*\n{escaped_summary}"
            )
            
            # Truncate if needed
            response_message = self.truncate_message(response_message)
            
            # Add menu buttons - THIS MESSAGE WILL BE PRESERVED
            keyboard = self.create_main_menu_keyboard()
            
            await processing_message.edit_text(
                response_message, 
                parse_mode='MarkdownV2',
                reply_markup=keyboard
            )
            
            logger.info(f"Summary delivered to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            
            error_message = (
                "❌ *Processing Failed*\n\n"
                "Sorry, I couldn't process your PDF\\. "
                "Please try with a different file\\.\n\n"
                "Make sure it's a valid PDF with readable text\\."
            )
            
            keyboard = self.create_main_menu_keyboard()
            
            try:
                if processing_message:
                    await processing_message.edit_text(
                        error_message, 
                        parse_mode='MarkdownV2',
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_text(
                        error_message, 
                        parse_mode='MarkdownV2',
                        reply_markup=keyboard
                    )
            except:
                # Final fallback
                await update.message.reply_text(
                    "❌ Processing Failed\n\nSorry, I couldn't process your PDF. Please try again."
                )

    async def _download_pdf(self, document: Document, user_id: int) -> str:
        """Download PDF file."""
        try:
            file = await document.get_file()
            file_name = f"{user_id}_{document.file_unique_id}.pdf"
            file_path = self.downloads_dir / file_name
            await file.download_to_drive(file_path)
            logger.info(f"PDF downloaded: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")

    async def _process_pdf_with_documents(self, documents, user_id: int) -> str:
        """Process PDF documents and generate summary."""
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Get prompt
            if user_id in self.user_prompts:
                prompt_template = self.user_prompts[user_id]
                logger.info(f"Using custom prompt for user {user_id}")
            else:
                prompt_template = self.default_prompt
                logger.info(f"Using default prompt for user {user_id}")
            
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            
            # Create chain
            summarize_chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                map_prompt=prompt,
                combine_prompt=prompt,
                verbose=False
            )
            
            # Generate summary
            logger.info("Starting AI summarization")
            summary_result = summarize_chain.invoke({"input_documents": chunks})
            
            logger.info("Summarization completed")
            
            # Extract summary
            if isinstance(summary_result, dict) and 'output_text' in summary_result:
                return summary_result['output_text'].strip()
            else:
                return str(summary_result).strip()
                
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")

    def _cleanup_file(self, file_path: str) -> None:
        """Clean up downloaded file."""
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    async def handle_non_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-document messages."""
        # Check if user is in prompt setting mode
        if context.user_data.get('setting_prompt'):
            return  # Let the conversation handler deal with it
            
        help_message = (
            "📄 *Send me a PDF file\\!*\n\n"
            "I can only work with PDF documents\\.\n"
            "Just send me any PDF file to get started\\!\n\n"
            "*File requirements:*\n"
            "• PDF format only\n"
            "• Maximum 20MB size"
        )
        
        keyboard = self.create_main_menu_keyboard()
        
        await update.message.reply_text(
            help_message, 
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )

    def run(self) -> None:
        """Start the bot with proper handlers."""
        try:
            application = Application.builder().token(self.telegram_token).build()
            
            # Conversation handler for prompt setting
            prompt_conversation = ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(self.button_callback, pattern="^set_prompt$")
                ],
                states={
                    WAITING_FOR_PROMPT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_custom_prompt)
                    ],
                },
                fallbacks=[CommandHandler("cancel", self.cancel_prompt_setting)],
            )
            
            # Register handlers in correct order
            application.add_handler(prompt_conversation)
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CallbackQueryHandler(self.button_callback))
            application.add_handler(MessageHandler(filters.Document.PDF, self.handle_document))
            application.add_handler(MessageHandler(
                filters.Document.ALL & ~filters.Document.PDF, 
                self.handle_non_document
            ))
            application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_non_document
            ))
            
            logger.info("PDF Summarizer Bot with Summary Preservation starting...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Failed to start: {str(e)}")
            raise


def main():
    """Main entry point."""
    try:
        bot = PDFSummarizerBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
