# ✈️ AI Travel Planner

An intelligent travel planning application that helps users find flights, hotels, and generate personalized travel itineraries using AI-powered recommendations. Built with Streamlit, FastAPI, and integrated with SerpAPI for real-time travel data and Google Gemini for AI recommendations.

## 🌟 Features

### 🛫 Flight Search
- Search for flights between airports
- Filter by departure date, return date, passengers, and cabin class
- Real-time flight prices and availability
- AI-powered flight recommendations based on price, duration, stops, and convenience
- Detailed flight information including airline, duration, stops, departure/arrival times

### 🏨 Hotel Search
- Search hotels by city or country
- Filter by check-in/check-out dates, number of guests, and room type
- Real-time hotel prices and availability
- AI-powered hotel recommendations based on price, rating, location, and amenities
- Detailed hotel information including ratings, amenities, location, and booking links

### 📅 Travel Itinerary Generator
- Generate personalized day-by-day travel itineraries
- Combine flight and hotel information
- AI-generated activity recommendations
- Includes must-visit attractions, restaurant suggestions, and transportation tips
- Beautiful markdown-formatted output with emojis and clear structure

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- SerpAPI account and API key ([Get one here](https://serpapi.com/))
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- OpenWeatherMap API key ([Get one here](https://openweathermap.org/api) - Free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AI TRAVEL PLANNER"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SERP_API_KEY=your_serpapi_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```
   
   **Getting API Keys:**
   - **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api) and get your free API key from the dashboard

### Running the Application

The application consists of two components:

#### 1. Backend API Server

Start the FastAPI backend server:

```bash
python travel_backend.py
```

The backend will run on `http://localhost:8000` by default.

You can also use uvicorn directly:
```bash
uvicorn travel_backend:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Streamlit App

In a separate terminal, start the Streamlit frontend:

```bash
streamlit run app.py
```

The frontend will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
AI TRAVEL PLANNER/
│
├── app.py                 # Streamlit frontend application
├── travel_backend.py      # FastAPI backend server
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🔧 Configuration

### API Configuration

The application requires two API keys:

1. **SerpAPI Key**: Used for fetching real-time flight and hotel data
   - Sign up at [serpapi.com](https://serpapi.com/)
   - Get your API key from the dashboard
   - Add to `.env` as `SERP_API_KEY`

2. **Google Gemini API Key**: Used for AI recommendations and itinerary generation
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to `.env` as `GEMINI_API_KEY`

3. **OpenWeatherMap API Key**: Used for weather information
   - Sign up at [openweathermap.org](https://openweathermap.org/api)
   - Get your free API key from the dashboard (free tier includes 1,000 calls/day)
   - Add to `.env` as `OPENWEATHER_API_KEY`

### Backend API URL

The frontend connects to the backend API. By default, it's set to `http://localhost:8000`. You can change this in the Streamlit sidebar or modify `API_BASE_URL` in `app.py`.

## 📖 Usage Guide

### Searching for Flights

1. Navigate to the **Flight Search** tab
2. Enter:
   - Origin airport code (e.g., JFK, LAX)
   - Destination airport code
   - Departure date
   - Optional: Return date, number of passengers, cabin class
3. Click **Search Flights**
4. Review AI recommendations and available flights
5. Click on individual flights for detailed information

### Searching for Hotels

1. Navigate to the **Hotel Search** tab
2. Enter:
   - Hotel location (city or country)
   - Check-in date
   - Check-out date
   - Number of guests
   - Room type (standard/deluxe)
3. Click **Search Hotels**
4. Review AI recommendations and available hotels
5. Click on individual hotels for detailed information

### Generating an Itinerary

1. Navigate to the **Generate Itinerary** tab
2. Enter:
   - Destination
   - Check-in and check-out dates
   - Paste flight details from your flight search
   - Paste hotel details from your hotel search
   - Select preferred activities (optional)
3. Click **Generate Itinerary**
4. Review your personalized travel plan

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SerpAPI**: Real-time search engine results API for flights and hotels
- **CrewAI**: AI agent framework for intelligent recommendations
- **Google Gemini**: Large language model for AI-powered analysis
- **Uvicorn**: ASGI server for running FastAPI

### Frontend
- **Streamlit**: Rapid web app development framework
- **Pandas**: Data manipulation and display
- **Requests**: HTTP library for API calls

## 🔍 API Endpoints

The backend provides the following endpoints:

### POST `/search_flights/`
Search for flights based on criteria.

**Request Body:**
```json
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2024-12-25",
  "return_date": "2024-12-30",
  "passengers": 1,
  "cabin_class": "economy",
  "preferences": []
}
```

**Response:**
```json
{
  "flights": [...],
  "ai_flight_recommendation": "..."
}
```

### POST `/search_hotels/`
Search for hotels based on criteria.

**Request Body:**
```json
{
  "location": "New York",
  "check_in_date": "2024-12-25",
  "check_out_date": "2024-12-30",
  "guests": 2,
  "room_type": "standard",
  "preferences": []
}
```

**Response:**
```json
{
  "hotels": [...],
  "ai_hotel_recommendation": "..."
}
```

### POST `/generate_itinerary/`
Generate a travel itinerary.

**Request Body:**
```json
{
  "destination": "New York",
  "check_in_date": "2024-12-25",
  "check_out_date": "2024-12-30",
  "flights": "...",
  "hotels": "...",
  "activities": []
}
```

**Response:**
```json
{
  "itinerary": "..."
}
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify API keys are set in `.env` file
- Check if port 8000 is already in use

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check the API URL in the Streamlit sidebar
- Verify firewall settings allow local connections

### No search results
- Verify your SerpAPI key is valid and has credits
- Check that your search criteria are valid (e.g., correct airport codes)
- Review backend logs for error messages

### AI recommendations not working
- Verify your Gemini API key is valid
- Check that CrewAI is properly installed
- Review backend logs for AI-related errors

## 📝 Requirements

Create a `requirements.txt` file with the following dependencies:

```
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
requests>=2.31.0
pandas>=2.1.0
python-dotenv>=1.0.0
serpapi>=0.1.5
crewai>=0.1.0
pydantic>=2.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [SerpAPI](https://serpapi.com/) for travel data
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI capabilities
- [CrewAI](https://github.com/joaomdmoura/crewAI) for AI agent framework
- [Streamlit](https://streamlit.io/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

## 📧 Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**Happy Travel Planning! ✈️🌍**

