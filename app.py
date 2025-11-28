import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

# Backend API URL
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✈️ AI Travel Planner")
st.markdown("Plan your perfect trip with AI-powered recommendations!")

# Sidebar for API configuration
st.sidebar.header("⚙️ Configuration")
api_url = st.sidebar.text_input("Backend API URL", value=API_BASE_URL)
if api_url != API_BASE_URL:
    API_BASE_URL = api_url

# Function to make API calls
def make_api_call(endpoint, data):
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["🛫 Flight Search", "🏨 Hotel Search", "📅 Generate Itinerary"])

with tab1:
    st.header("🛫 Search Flights")

    col1, col2 = st.columns(2)

    with col1:
        origin = st.text_input("Origin Airport Code (e.g., JFK)", key="flight_origin").upper()
        destination = st.text_input("Destination Airport Code (e.g., LAX)", key="flight_dest").upper()
        departure_date = st.date_input("Departure Date", min_value=datetime.today(), key="flight_depart")

    with col2:
        return_date = st.date_input("Return Date (Optional)", key="flight_return", value=None)
        passengers = st.number_input("Number of Passengers", min_value=1, max_value=9, value=1, key="flight_passengers")
        cabin_class = st.selectbox("Cabin Class", ["economy", "business"], key="flight_class")

    preferences = st.multiselect(
        "Flight Preferences (Optional)",
        ["Direct flights only", "Morning departure", "Evening departure", "Budget friendly"],
        key="flight_prefs"
    )

    if st.button("🔍 Search Flights", key="search_flights"):
        if not origin or not destination:
            st.error("Please enter both origin and destination airport codes.")
        else:
            flight_data = {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date.strftime("%Y-%m-%d"),
                "return_date": return_date.strftime("%Y-%m-%d") if return_date else None,
                "passengers": passengers,
                "cabin_class": cabin_class,
                "preferences": preferences
            }

            with st.spinner("Searching for flights..."):
                result = make_api_call("/search_flights/", flight_data)

            if result:
                # Display AI Recommendation
                if result.get("ai_flight_recommendation"):
                    st.subheader("🤖 AI Flight Recommendation")
                    st.info(result["ai_flight_recommendation"])

                # Display Flights
                if result.get("flights"):
                    st.subheader("Available Flights")
                    flights_df = pd.DataFrame(result["flights"])
                    st.dataframe(flights_df, use_container_width=True)

                    # Display individual flight cards
                    for i, flight in enumerate(result["flights"], 1):
                        # Build title with available data
                        title_parts = []
                        if flight.get('airline'):
                            title_parts.append(flight.get('airline'))
                        if flight.get('price'):
                            title_parts.append(flight.get('price'))
                        title = f"Flight {i}: {' - '.join(title_parts)}" if title_parts else f"Flight {i}"
                        
                        with st.expander(title):
                            col1, col2 = st.columns(2)
                            with col1:
                                if flight.get('airline'):
                                    st.write(f"**Airline:** {flight.get('airline')}")
                                if flight.get('price'):
                                    st.write(f"**Price:** {flight.get('price')}")
                                if flight.get('duration'):
                                    st.write(f"**Duration:** {flight.get('duration')}")
                                if flight.get('stops'):
                                    st.write(f"**Stops:** {flight.get('stops')}")
                            with col2:
                                if flight.get('departure'):
                                    st.write(f"**Departure:** {flight.get('departure')}")
                                if flight.get('arrival'):
                                    st.write(f"**Arrival:** {flight.get('arrival')}")
                                if flight.get('travel_class'):
                                    st.write(f"**Class:** {flight.get('travel_class')}")
                                if flight.get('booking_link'):
                                    st.markdown(f"[Book Now]({flight.get('booking_link')})")
                else:
                    st.warning("No flights found for your search criteria.")

with tab2:
    st.header("🏨 Search Hotels")

    col1, col2 = st.columns(2)

    with col1:
        location = st.text_input("Hotel Location (City/Country)", key="hotel_location")
        check_in_date = st.date_input("Check-in Date", min_value=datetime.today(), key="hotel_checkin")

    with col2:
        check_out_date = st.date_input("Check-out Date", min_value=check_in_date + timedelta(days=1), key="hotel_checkout")
        guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=1, key="hotel_guests")
        room_type = st.selectbox("Room Type", ["standard", "deluxe"], key="hotel_room")

    preferences = st.multiselect(
        "Hotel Preferences (Optional)",
        ["Free WiFi", "Pool", "Gym", "Breakfast included", "Pet friendly", "City center"],
        key="hotel_prefs"
    )

    if st.button("🔍 Search Hotels", key="search_hotels"):
        if not location:
            st.error("Please enter a hotel location.")
        else:
            hotel_data = {
                "location": location,
                "check_in_date": check_in_date.strftime("%Y-%m-%d"),
                "check_out_date": check_out_date.strftime("%Y-%m-%d"),
                "guests": guests,
                "room_type": room_type,
                "preferences": preferences
            }

            with st.spinner("Searching for hotels..."):
                result = make_api_call("/search_hotels/", hotel_data)

            if result:
                # Display AI Recommendation
                if result.get("ai_hotel_recommendation"):
                    st.subheader("🤖 AI Hotel Recommendation")
                    st.info(result["ai_hotel_recommendation"])

                # Display Hotels
                if result.get("hotels"):
                    st.subheader("Available Hotels")
                    hotels_df = pd.DataFrame(result["hotels"])
                    st.dataframe(hotels_df, use_container_width=True)

                    # Display individual hotel cards
                    for i, hotel in enumerate(result["hotels"], 1):
                        # Build title with available data - prioritize name, price, and location
                        title_parts = []
                        if hotel.get('name'):
                            title_parts.append(hotel.get('name'))
                        if hotel.get('price_per_night'):
                            title_parts.append(hotel.get('price_per_night'))
                        title = f"Hotel {i}: {' - '.join(title_parts)}" if title_parts else f"Hotel {i}"
                        
                        with st.expander(title):
                            col1, col2 = st.columns(2)
                            with col1:
                                if hotel.get('name'):
                                    st.write(f"**Name:** {hotel.get('name')}")
                                if hotel.get('price_per_night'):
                                    st.write(f"**Price/Night:** {hotel.get('price_per_night')}")
                                if hotel.get('location'):
                                    st.write(f"**Location:** {hotel.get('location')}")
                                if hotel.get('rating'):
                                    st.write(f"**Rating:** {hotel.get('rating')}")
                            with col2:
                                if hotel.get('check_in'):
                                    st.write(f"**Check-in:** {hotel.get('check_in')}")
                                if hotel.get('check_out'):
                                    st.write(f"**Check-out:** {hotel.get('check_out')}")
                                amenities = hotel.get('amenities', [])
                                if amenities:
                                    st.write(f"**Amenities:** {', '.join(amenities)}")
                                if hotel.get('booking_link'):
                                    st.markdown(f"[Book Now]({hotel.get('booking_link')})")
                else:
                    st.warning("No hotels found for your search criteria.")

with tab3:
    st.header("📅 Generate Travel Itinerary")

    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input("Destination", key="itinerary_dest")
        check_in_date = st.date_input("Check-in Date", min_value=datetime.today(), key="itinerary_checkin")

    with col2:
        check_out_date = st.date_input("Check-out Date", min_value=check_in_date + timedelta(days=1), key="itinerary_checkout")

    st.subheader("Flight Information")
    flights_text = st.text_area(
        "Paste flight details here (from your flight search results)",
        height=100,
        key="itinerary_flights",
        placeholder="Copy and paste the flight information you want to include in your itinerary..."
    )

    st.subheader("Hotel Information")
    hotels_text = st.text_area(
        "Paste hotel details here (from your hotel search results)",
        height=100,
        key="itinerary_hotels",
        placeholder="Copy and paste the hotel information you want to include in your itinerary..."
    )

    activities = st.multiselect(
        "Preferred Activities (Optional)",
        ["Sightseeing", "Adventure", "Cultural", "Food & Dining", "Shopping", "Relaxation", "Nightlife"],
        key="itinerary_activities"
    )

    if st.button("🎯 Generate Itinerary", key="generate_itinerary"):
        if not destination or not flights_text or not hotels_text:
            st.error("Please fill in destination, flight details, and hotel details.")
        else:
            itinerary_data = {
                "destination": destination,
                "check_in_date": check_in_date.strftime("%Y-%m-%d"),
                "check_out_date": check_out_date.strftime("%Y-%m-%d"),
                "flights": flights_text,
                "hotels": hotels_text,
                "activities": activities
            }

            with st.spinner("Generating your personalized itinerary..."):
                result = make_api_call("/generate_itinerary/", itinerary_data)

            if result and result.get("itinerary"):
                st.subheader("📋 Your Travel Itinerary")
                st.markdown(result["itinerary"])
            else:
                st.error("Failed to generate itinerary. Please try again.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and AI-powered travel planning")
st.markdown("*Make sure your backend server is running on http://localhost:8000*")
