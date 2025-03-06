# Flask Chat Application with Azure OpenAI

A modern chat application built with Flask that integrates with Azure OpenAI to provide AI-powered responses in a clean, responsive interface.

## Features

- **Thread-based Chat Interface**: Create and manage multiple conversation threads
- **Azure OpenAI Integration**: Get AI-powered responses using Azure OpenAI's services
- **Dark/Light Mode Support**: Toggle between dark and light themes for comfortable viewing
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **User Authentication**: Secure login and user account management
- **MySQL Database**: Efficiently stores chat threads and message history

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: MySQL with Flask-SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI Integration**: Azure OpenAI API
- **Authentication**: Flask session management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/waxwaxwax/flaskchatapp.git
   cd flaskchatapp
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows, use: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   
   # Database
   MYSQL_HOST=localhost
   MYSQL_USER=your_db_username
   MYSQL_PASSWORD=your_db_password
   MYSQL_DATABASE=flaskchat
   
   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_MODEL=your_model_deployment_name
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

7. Access the application in your browser at `http://127.0.0.1:5000`

## Usage

1. **Registration/Login**: Create an account or log in to an existing one
2. **Creating a Thread**: Click the new thread button (pen icon) to start a new conversation
3. **Sending Messages**: Type your message in the input field and press Send or Enter
4. **Thread Management**: Select different threads from the sidebar to switch between conversations
5. **Theme Toggle**: Use the moon/sun icon in the navbar to switch between dark and light modes

## Application Structure

- `app.py`: Main application file with route definitions
- `models.py`: Database models for users, threads, and messages
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and image files
- `utils/`: Utility functions including AI integration
- `migrations/`: Database migration files

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask framework and its extensions
- Azure OpenAI for providing the AI capabilities
- Tailwind CSS for the responsive design
