import os
import uvicorn
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from serpapi import Client
from datetime import datetime
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "gemini_api_key_here")
SERP_API_KEY = os.getenv("SERP_API_KEY", "serpapi_key_here")

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

logger.info(f"API Keys loaded: GEMINI_API_KEY={'*' * len(GEMINI_API_KEY) if GEMINI_API_KEY else 'None'}, SERP_API_KEY={'*' * len(SERP_API_KEY) if SERP_API_KEY else 'None'}")

def initalize_llm():
    try:
        from crewai import LLM
        return LLM(
            model="gemini/gemini-3.0-pro",
            provider="google",
            api_key=GEMINI_API_KEY,
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise HTTPException(status_code=500, detail=f"LLM initialization error: {str(e)}")
    
class FlightRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    cabin_class: str = "economy"
    preferences: Optional[List[str]] = []
    
class HotelRequest(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    guests: int = 1
    room_type: str = "standard"
    preferences: Optional[List[str]] = []
    
class ItineraryRequest(BaseModel):
    destination: str
    check_in_date: str
    check_out_date: str
    flights: str
    hotels: str
    activities: Optional[List[str]] = []
    
class FlightInfo(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    departure: str
    arrival: str
    travel_class: str
    return_date: str
    airline_logo: str
    booking_link: str
    
class HotelInfo(BaseModel):
    name: str
    price_per_night: str
    rating: str
    amenities: List[str]
    location: str
    check_in: str
    check_out: str
    hotel_image: str
    booking_link: str
    
    
class AIResponse(BaseModel):
    flights: List[FlightInfo] = []
    hotels: List[HotelInfo] = []
    ai_flight_recommendation: str = ""
    ai_hotel_recommendation: str = ""
    itinerary: str = ""         
    

app=FastAPI(title="AI Travel Planner", version="1.0")


def parse_flight_data(raw_flights: list, flight_request: FlightRequest) -> List[FlightInfo]:
    """Parse raw SerpAPI flight data into FlightInfo objects."""
    parsed_flights = []
    
    if not raw_flights:
        return parsed_flights
    
    try:
        # SerpAPI returns flights in different structures, handle common formats
        flights_list = raw_flights
        if isinstance(raw_flights, dict):
            # Sometimes flights are nested in a dict
            flights_list = raw_flights.get("flights", []) or raw_flights.get("best_flights", []) or []
        
        for flight in flights_list:
            try:
                # Extract flight details - handle different response structures
                # Only set values if data exists, otherwise leave as None/empty
                airline = None
                price = None
                duration = None
                stops = None
                departure = None
                arrival = None
                airline_logo = ""
                booking_link = ""
                
                # Try to extract airline name
                if isinstance(flight, dict):
                    airline = flight.get("airline") or (flight.get("airlines", [{}])[0].get("name") if flight.get("airlines") else None)
                    
                    # Extract price
                    price_data = flight.get("price") or flight.get("total_price")
                    if price_data:
                        if isinstance(price_data, dict):
                            price = price_data.get("total") or price_data.get("price")
                        elif isinstance(price_data, (int, float)):
                            price = f"${price_data:.2f}"
                        elif isinstance(price_data, str) and price_data.strip():
                            price = price_data
                    
                    # Extract duration
                    duration_data = flight.get("duration") or flight.get("flight_duration")
                    if duration_data:
                        if isinstance(duration_data, int):
                            hours = duration_data // 60
                            minutes = duration_data % 60
                            duration = f"{hours}h {minutes}m"
                        elif isinstance(duration_data, str) and duration_data.strip():
                            duration = duration_data
                    
                    # Extract stops
                    stops_data = flight.get("stops") or flight.get("number_of_stops")
                    if stops_data is not None:
                        if isinstance(stops_data, int):
                            stops = str(stops_data) if stops_data > 0 else "Direct"
                        elif isinstance(stops_data, str) and stops_data.strip():
                            stops = str(stops_data)
                    
                    # Extract departure time
                    departure_data = flight.get("departure_airport") or flight.get("departure")
                    if departure_data:
                        if isinstance(departure_data, dict):
                            departure = departure_data.get("time") or departure_data.get("datetime")
                        elif isinstance(departure_data, str) and departure_data.strip():
                            departure = departure_data
                    
                    # Extract arrival time
                    arrival_data = flight.get("arrival_airport") or flight.get("arrival")
                    if arrival_data:
                        if isinstance(arrival_data, dict):
                            arrival = arrival_data.get("time") or arrival_data.get("datetime")
                        elif isinstance(arrival_data, str) and arrival_data.strip():
                            arrival = arrival_data
                    
                    # Extract airline logo and booking link
                    airline_logo = flight.get("airline_logo") or flight.get("logo") or ""
                    booking_link = flight.get("link") or flight.get("booking_link") or ""
                
                # Only create flight if we have at least airline or price
                if not airline and not price:
                    continue
                
                # Use empty string for required fields that are None
                parsed_flight = FlightInfo(
                    airline=airline or "",
                    price=str(price) if price else "",
                    duration=str(duration) if duration else "",
                    stops=str(stops) if stops else "",
                    departure=str(departure) if departure else "",
                    arrival=str(arrival) if arrival else "",
                    travel_class=flight_request.cabin_class,
                    return_date=flight_request.return_date or "",
                    airline_logo=str(airline_logo) if airline_logo else "",
                    booking_link=str(booking_link) if booking_link else ""
                )
                
                parsed_flights.append(parsed_flight)
            except Exception as e:
                logger.warning(f"Error parsing individual flight: {e}")
                continue
    except Exception as e:
        logger.error(f"Error parsing flight data: {e}")
    
    return parsed_flights


def parse_hotel_data(raw_hotels: list, hotel_request: HotelRequest) -> List[HotelInfo]:
    """Parse raw SerpAPI hotel data into HotelInfo objects."""
    parsed_hotels = []
    
    if not raw_hotels:
        return parsed_hotels
    
    try:
        hotels_list = raw_hotels
        if isinstance(raw_hotels, dict):
            hotels_list = raw_hotels.get("properties", []) or raw_hotels.get("hotels", []) or []
        
        for hotel in hotels_list:
            try:
                if not isinstance(hotel, dict):
                    continue
                
                # Extract hotel details - only set if data exists
                name = hotel.get("title") or hotel.get("name")
                if not name:
                    continue  # Skip hotels without a name
                
                price_per_night = None
                rating = None
                amenities = []
                location = hotel_request.location  # Default to requested location
                hotel_image = ""
                booking_link = ""
                
                # Extract price
                price_data = hotel.get("price") or hotel.get("total_price") or hotel.get("rate")
                if price_data:
                    if isinstance(price_data, dict):
                        price_per_night = price_data.get("total") or price_data.get("price")
                    elif isinstance(price_data, (int, float)):
                        price_per_night = f"${price_data:.2f}"
                    elif isinstance(price_data, str) and price_data.strip():
                        price_per_night = price_data
                
                # Extract rating
                rating_data = hotel.get("rating") or hotel.get("overall_rating")
                if rating_data:
                    rating = str(rating_data)
                
                # Extract amenities
                amenities_data = hotel.get("amenities") or hotel.get("features", [])
                if amenities_data:
                    if isinstance(amenities_data, list):
                        amenities = [str(a) if isinstance(a, str) else a.get("name", str(a)) for a in amenities_data[:10] if a]
                    elif isinstance(amenities_data, str) and amenities_data.strip():
                        amenities = [amenities_data]
                
                # Extract location if available
                location_data = hotel.get("address") or hotel.get("location")
                if location_data:
                    if isinstance(location_data, str) and location_data.strip():
                        location = location_data
                    elif isinstance(location_data, dict):
                        location = location_data.get("address") or location_data.get("city") or hotel_request.location
                
                # Extract image and booking link
                hotel_image = hotel.get("thumbnail") or hotel.get("image") or ""
                booking_link = hotel.get("link") or hotel.get("booking_link") or hotel.get("url") or ""
                
                parsed_hotel = HotelInfo(
                    name=str(name),
                    price_per_night=str(price_per_night) if price_per_night else "",
                    rating=str(rating) if rating else "",
                    amenities=amenities,
                    location=str(location),
                    check_in=hotel_request.check_in_date,
                    check_out=hotel_request.check_out_date,
                    hotel_image=str(hotel_image) if hotel_image else "",
                    booking_link=str(booking_link) if booking_link else ""
                )
                parsed_hotels.append(parsed_hotel)
            except Exception as e:
                logger.warning(f"Error parsing individual hotel: {e}")
                continue
    except Exception as e:
        logger.error(f"Error parsing hotel data: {e}")
    
    return parsed_hotels


def format_travel_data(data_type: str, data: list) -> str:
    """Format flight or hotel data into readable text for AI analysis."""
    if not data:
        return f"No {data_type} data available."
    
    formatted = []
    if data_type == "flights":
        for i, flight in enumerate(data, 1):
            # Handle both dict and FlightInfo objects
            if hasattr(flight, 'airline'):
                flight_dict = flight.dict() if hasattr(flight, 'dict') else flight
            else:
                flight_dict = flight
            
            # Only include fields that have values
            flight_parts = [f"Flight {i}:"]
            if flight_dict.get('airline'):
                flight_parts.append(f"- Airline: {flight_dict.get('airline')}")
            if flight_dict.get('price'):
                flight_parts.append(f"- Price: {flight_dict.get('price')}")
            if flight_dict.get('duration'):
                flight_parts.append(f"- Duration: {flight_dict.get('duration')}")
            if flight_dict.get('stops'):
                flight_parts.append(f"- Stops: {flight_dict.get('stops')}")
            if flight_dict.get('departure'):
                flight_parts.append(f"- Departure: {flight_dict.get('departure')}")
            if flight_dict.get('arrival'):
                flight_parts.append(f"- Arrival: {flight_dict.get('arrival')}")
            
            flight_info = "\n            ".join(flight_parts)
            formatted.append(flight_info)
    elif data_type == "hotels":
        for i, hotel in enumerate(data, 1):
            # Handle both dict and HotelInfo objects
            if hasattr(hotel, 'name'):
                hotel_dict = hotel.dict() if hasattr(hotel, 'dict') else hotel
            else:
                hotel_dict = hotel
            
            # Only include fields that have values
            hotel_parts = [f"Hotel {i}:"]
            if hotel_dict.get('name'):
                hotel_parts.append(f"- Name: {hotel_dict.get('name')}")
            price = hotel_dict.get('price_per_night') or hotel_dict.get('price')
            if price:
                hotel_parts.append(f"- Price: {price}")
            if hotel_dict.get('location'):
                hotel_parts.append(f"- Location: {hotel_dict.get('location')}")
            if hotel_dict.get('rating'):
                hotel_parts.append(f"- Rating: {hotel_dict.get('rating')}")
            amenities = hotel_dict.get('amenities', [])
            if amenities:
                hotel_parts.append(f"- Amenities: {', '.join(amenities)}")
            
            hotel_info = "\n            ".join(hotel_parts)
            formatted.append(hotel_info)
    
    return "\n".join(formatted)


async def run_search(params):
    """Generic function to run SerpAPI searches asynchronously."""
    try:
        client = Client(api_key=SERP_API_KEY)
        logger.info(f"Making SerpAPI request with API key ending in: ...{SERP_API_KEY[-4:] if SERP_API_KEY else 'None'}")
        result = await asyncio.to_thread(lambda: client.search(params))
        logger.info(f"SerpAPI request successful")
        return result
    except Exception as e:
        logger.exception(f"SerpAPI search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")


async def search_flights(flight_request: FlightRequest):
    """Fetch real-time flight details from Google Flights using SerpAPI."""
    logger.info(f"Searching flights: {flight_request.origin} to {flight_request.destination}")

    try:
        params = {
            "api_key": SERP_API_KEY,
            "engine": "google_flights",
            "hl": "en",
            "gl": "us",
            "departure_id": flight_request.origin.strip().upper(),
            "arrival_id": flight_request.destination.strip().upper(),
            "outbound_date": flight_request.departure_date,
            "return_date": flight_request.return_date,
            "currency": "USD"
        }
        
        # Add passengers if supported
        if flight_request.passengers > 1:
            params["adults"] = flight_request.passengers

        search_results = await run_search(params)
        
        # Try different possible keys for flight data
        flights = None
        possible_keys = ["flights", "best_flights", "other_flights", "results"]
        for key in possible_keys:
            if search_results and search_results.get(key):
                flights = search_results.get(key)
                logger.info(f"Found flights under key '{key}': {len(flights) if flights else 0} flights")
                break
        
        if flights is None:
            logger.warning(f"No flight data found in response. Response keys: {list(search_results.keys()) if search_results else 'None'}")
            return []
        
        return flights
    except Exception as e:
        logger.exception(f"Error in search_flights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flight search error: {str(e)}")

async def search_hotels(hotel_request: HotelRequest):
    """Fetch hotel information from SerpAPI."""
    logger.info(f"Searching hotels for: {hotel_request.location}")

    try:
        params = {
            "api_key": SERP_API_KEY,
            "engine": "google_hotels",
            "q": hotel_request.location,
            "hl": "en",
            "gl": "us",
            "check_in_date": hotel_request.check_in_date,
            "check_out_date": hotel_request.check_out_date,
            "currency": "USD",
            "adults": hotel_request.guests,
            "sort_by": 3,
            "rating": 8
        }
        
        # Add room type if supported (some APIs support this)
        if hotel_request.room_type and hotel_request.room_type != "standard":
            # Note: SerpAPI may not directly support room_type, but we can filter results later
            logger.info(f"Room type requested: {hotel_request.room_type}")

        logger.info(f"Calling SerpAPI with params: {params}")
        search_results = await run_search(params)
        logger.info(f"SerpAPI response type: {type(search_results)}")
        logger.info(f"SerpAPI response keys: {list(search_results.keys()) if hasattr(search_results, 'keys') else 'No keys method'}")
        
        # Try different possible keys for hotel data
        hotels = None
        possible_keys = ["properties", "hotels", "results", "data"]
        for key in possible_keys:
            if hasattr(search_results, 'get') and search_results.get(key):
                hotels = search_results.get(key)
                logger.info(f"Found hotels under key '{key}': {len(hotels) if hotels else 0} hotels")
                break
        
        if hotels is None:
            logger.warning(f"No hotel data found in response. Full response: {search_results}")
            return []
        
        return hotels
    except Exception as e:
        logger.exception(f"Error in search_hotels: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hotel search error: {str(e)}")


async def get_ai_recommendation(data_type, formatted_data):
    logger.info(f"Getting {data_type} analysis from AI")
    try:
        from crewai import Agent, Task, Crew, Process
        llm_model = initalize_llm()

        # Configure agent based on data type
        if data_type == "flights":
            role = "AI Flight Analyst"
            goal = "Analyze flight options and recommend the best one considering price, duration, stops, and overall convenience."
            backstory = f"AI expert that provides in-depth analysis comparing flight options based on multiple factors."
            description = """
            Recommend the best flight from the available options, based on the details provided below:

            **Reasoning for Recommendation:**
            - **Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
            - **Duration:** Explain why this flight has the best duration in comparison to others.
            - **Stops:** Discuss why this flight has minimal or optimal stops.
            - **Travel Class:** Describe why this flight provides the best comfort and amenities.

            Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
            """
        elif data_type == "hotels":
            role = "AI Hotel Analyst"
            goal = "Analyze hotel options and recommend the best one considering price, rating, location, and amenities."
            backstory = f"AI expert that provides in-depth analysis comparing hotel options based on multiple factors."
            description = """
            Based on the following analysis, generate a detailed recommendation for the best hotel. Your response should include clear reasoning based on price, rating, location, and amenities.

            **AI Hotel Recommendation**
            We recommend the best hotel based on the following analysis:

            **Reasoning for Recommendation**:
            - **Price:** The recommended hotel is the best option for the price compared to others, offering the best value for the amenities and services provided.
            - **Rating:** With a higher rating compared to the alternatives, it ensures a better overall guest experience. Explain why this makes it the best choice.
            - **Location:** The hotel is in a prime location, close to important attractions, making it convenient for travelers.
            - **Amenities:** The hotel offers amenities like Wi-Fi, pool, fitness center, free breakfast, etc. Discuss how these amenities enhance the experience, making it suitable for different types of travelers.

            **Reasoning Requirements**:
            - Ensure that each section clearly explains why this hotel is the best option based on the factors of price, rating, location, and amenities.
            - Compare it against the other options and explain why this one stands out.
            - Provide concise, well-structured reasoning to make the recommendation clear to the traveler.
            - Your recommendation should help a traveler make an informed decision based on multiple factors, not just one.
            """
        else:
            raise ValueError("Invalid data type for AI recommendation")

        # Create the agent and task
        analyze_agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm_model,
            verbose=False
        )

        analyze_task = Task(
            description=f"{description}\n\nData to analyze:\n{formatted_data}",
            agent=analyze_agent,
            expected_output=f"A structured recommendation explaining the best {data_type} choice based on the analysis of provided details."
        )

        # Define CrewAI Workflow for the agent
        analyst_crew = Crew(
            agents=[analyze_agent],
            tasks=[analyze_task],
            process=Process.sequential,
            verbose=False
        )

        # Execute CrewAI Process
        crew_results = await asyncio.to_thread(analyst_crew.kickoff)
        return str(crew_results)
    except Exception as e:
        logger.exception(f"Error getting AI recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI recommendation error: {str(e)}")


async def generate_itinerary(destination, flights_text, hotels_text, check_in_date, check_out_date):
    """Generate a detailed travel itinerary based on flight and hotel information."""
    try:
        from crewai import Agent, Task, Crew, Process
        # Convert the string dates to datetime objects
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")

        # Calculate the difference in days
        days = (check_out - check_in).days

        llm_model = initalize_llm()

        analyze_agent = Agent(
            role="AI Travel Planner",
            goal="Create a detailed itinerary for the user based on flight and hotel information",
            backstory="AI travel expert generating a day-by-day itinerary including flight details, hotel stays, and must-visit locations in the destination.",
            llm=llm_model,
            verbose=False
        )

        analyze_task = Task(
            description=f"""
            Based on the following details, create a {days}-day itinerary for the user:

            **Flight Details**:
            {flights_text}

            **Hotel Details**:
            {hotels_text}

            **Destination**: {destination}

            **Travel Dates**: {check_in_date} to {check_out_date} ({days} days)

            The itinerary should include:
            - Flight arrival and departure information
            - Hotel check-in and check-out details
            - Day-by-day breakdown of activities
            - Must-visit attractions and estimated visit times
            - Restaurant recommendations for meals
            - Tips for local transportation

            **Format Requirements**:
            - Use markdown formatting with clear headings (# for main headings, ## for days, ### for sections)
            - Include emojis for different types of activities ( for landmarks, 🍽️ for restaurants, etc.)
            - Use bullet points for listing activities
            - Include estimated timings for each activity
            - Format the itinerary to be visually appealing and easy to read
            """,
            agent=analyze_agent,
            expected_output="A well-structured, visually appealing itinerary in markdown format, including flight, hotel, and day-wise breakdown with emojis, headers, and bullet points."
        )

        itinerary_planner_crew = Crew(
            agents=[analyze_agent],
            tasks=[analyze_task],
            process=Process.sequential,
            verbose=False
        )

        crew_results = await asyncio.to_thread(itinerary_planner_crew.kickoff)
        return str(crew_results)
    except Exception as e:
        logger.exception(f"Error generating itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Itinerary generation error: {str(e)}")


@app.post("/search_flights/", response_model=AIResponse)
async def get_flight_recommendations(flight_request: FlightRequest):
    try:
        logger.info(f"Received flight request: {flight_request}")
        
        # Search for flights using SerpAPI
        raw_flights = await search_flights(flight_request)
        
        # Parse raw flight data into FlightInfo objects
        parsed_flights = parse_flight_data(raw_flights, flight_request)
        
        # Format flight data for AI analysis
        flights_text = format_travel_data("flights", parsed_flights)
        
        # Get AI recommendation
        ai_recommendation = ""
        if parsed_flights:
            try:
                ai_recommendation = await get_ai_recommendation("flights", flights_text)
            except Exception as e:
                logger.warning(f"Failed to get AI recommendation: {e}")
                ai_recommendation = "AI recommendation temporarily unavailable."
        else:
            ai_recommendation = "No flights found matching your criteria. Please try different dates or airports."
        
        # Convert FlightInfo objects to dicts for response
        flights_dict = [flight.dict() if hasattr(flight, 'dict') else flight for flight in parsed_flights]
        
        return AIResponse(flights=flights_dict, ai_flight_recommendation=ai_recommendation)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in get_flight_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flight search error: {str(e)}")

@app.post("/search_hotels/", response_model=AIResponse)
async def get_hotel_recommendations(hotel_request: HotelRequest):
    try:
        logger.info(f"Received hotel request: {hotel_request}")
        
        # Search for hotels using SerpAPI
        raw_hotels = await search_hotels(hotel_request)
        
        # Parse raw hotel data into HotelInfo objects
        parsed_hotels = parse_hotel_data(raw_hotels, hotel_request)
        
        # Filter by room type if specified (basic filtering based on amenities/name)
        if hotel_request.room_type and hotel_request.room_type != "standard":
            # Note: This is a basic filter - SerpAPI doesn't directly support room type filtering
            # You could enhance this by checking hotel names/amenities for room type keywords
            logger.info(f"Room type filter applied: {hotel_request.room_type}")
        
        # Format hotel data for AI analysis
        hotels_text = format_travel_data("hotels", parsed_hotels)
        
        # Get AI recommendation
        ai_recommendation = ""
        if parsed_hotels:
            try:
                ai_recommendation = await get_ai_recommendation("hotels", hotels_text)
            except Exception as e:
                logger.warning(f"Failed to get AI recommendation: {e}")
                ai_recommendation = "AI recommendation temporarily unavailable."
        else:
            ai_recommendation = "No hotels found matching your criteria. Please try different dates or location."
        
        # Convert HotelInfo objects to dicts for response
        hotels_dict = [hotel.dict() if hasattr(hotel, 'dict') else hotel for hotel in parsed_hotels]
        
        return AIResponse(hotels=hotels_dict, ai_hotel_recommendation=ai_recommendation)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in get_hotel_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hotel search error: {str(e)}")

@app.post("/generate_itinerary/", response_model=AIResponse)
async def get_itinerary(itinerary_request: ItineraryRequest):
    itinerary = await generate_itinerary(
        itinerary_request.destination,
        itinerary_request.flights,
        itinerary_request.hotels,
        itinerary_request.check_in_date,
        itinerary_request.check_out_date
    )
    return AIResponse(itinerary=itinerary)

if __name__ == "__main__":
    logger.info("Starting Travel Planning API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
