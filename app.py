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

# Initialize session state for favorites
if 'favorite_flights' not in st.session_state:
    st.session_state.favorite_flights = []
if 'favorite_hotels' not in st.session_state:
    st.session_state.favorite_hotels = []

# Create tabs for different functionalities
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🛫 Flight Search", 
    "🏨 Hotel Search", 
    "📅 Generate Itinerary",
    "💰 Budget Calculator",
    "✅ Travel Checklist",
    "💱 Currency Converter",
    "⭐ Favorites"
])

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
                            
                            # Add to favorites button
                            if st.button(f"⭐ Add to Favorites", key=f"fav_flight_{i}"):
                                if flight not in st.session_state.favorite_flights:
                                    st.session_state.favorite_flights.append(flight)
                                    st.success("Flight added to favorites!")
                                    st.rerun()
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

                # Weather information for location
                if location:
                    with st.spinner("Fetching weather information..."):
                        weather_data = {
                            "location": location,
                            "date": check_in_date.strftime("%Y-%m-%d")
                        }
                        weather_result = make_api_call("/get_weather/", weather_data)
                        if weather_result and weather_result.get("temperature"):
                            st.info(f"🌤️ Weather for {location} on {check_in_date.strftime('%B %d, %Y')}: {weather_result.get('temperature', 'N/A')}°F - {weather_result.get('condition', 'N/A')}")

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
                            
                            # Add to favorites button
                            if st.button(f"⭐ Add to Favorites", key=f"fav_hotel_{i}"):
                                if hotel not in st.session_state.favorite_hotels:
                                    st.session_state.favorite_hotels.append(hotel)
                                    st.success("Hotel added to favorites!")
                                    st.rerun()
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
                
                # Export itinerary button
                itinerary_text = result["itinerary"]
                st.download_button(
                    label="📥 Download Itinerary",
                    data=itinerary_text,
                    file_name=f"itinerary_{destination}_{check_in_date.strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            else:
                st.error("Failed to generate itinerary. Please try again.")

with tab4:
    st.header("💰 Budget Calculator")
    st.markdown("Calculate your total trip budget including flights, hotels, and daily expenses.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Flight Costs")
        flight_price = st.text_input("Flight Price (per person)", placeholder="e.g., $500", key="budget_flight")
        flight_passengers = st.number_input("Number of Passengers", min_value=1, max_value=10, value=1, key="budget_passengers")
        
        st.subheader("Hotel Costs")
        hotel_price = st.text_input("Hotel Price per Night", placeholder="e.g., $150", key="budget_hotel")
        nights = st.number_input("Number of Nights", min_value=1, max_value=365, value=1, key="budget_nights")
    
    with col2:
        st.subheader("Daily Expenses")
        daily_budget = st.number_input("Daily Budget (Food, Activities, etc.)", min_value=0.0, value=100.0, step=10.0, key="budget_daily")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"], key="budget_currency")
    
    if st.button("💰 Calculate Total Budget", key="calculate_budget"):
        budget_data = {
            "flight_price": flight_price if flight_price else None,
            "hotel_price_per_night": hotel_price if hotel_price else None,
            "nights": nights,
            "passengers": flight_passengers,
            "daily_budget": daily_budget,
            "currency": currency
        }
        
        with st.spinner("Calculating budget..."):
            result = make_api_call("/calculate_budget/", budget_data)
        
        if result:
            st.success(f"**{result.get('summary', 'Budget calculated')}**")
            
            st.subheader("📊 Budget Breakdown")
            breakdown = result.get("breakdown", {})
            
            if "flights" in breakdown:
                flight_info = breakdown["flights"]
                if "total" in flight_info:
                    st.write(f"**Flights:** ${flight_info['total']:,.2f} ({flight_info['passengers']} passengers × ${flight_info['per_person']:,.2f})")
            
            if "hotel" in breakdown:
                hotel_info = breakdown["hotel"]
                if "total" in hotel_info:
                    st.write(f"**Hotel:** ${hotel_info['total']:,.2f} ({hotel_info['nights']} nights × ${hotel_info['per_night']:,.2f}/night)")
            
            if "daily_expenses" in breakdown:
                daily_info = breakdown["daily_expenses"]
                st.write(f"**Daily Expenses:** ${daily_info['total']:,.2f} ({daily_info['days']} days × ${daily_info['per_day']:,.2f}/day)")
            
            st.metric("Total Trip Cost", f"${result.get('total_cost', 0):,.2f} {currency}")

with tab5:
    st.header("✅ Travel Checklist Generator")
    st.markdown("Get an AI-powered personalized packing checklist for your trip.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        checklist_destination = st.text_input("Destination", key="checklist_dest")
        duration = st.number_input("Trip Duration (days)", min_value=1, max_value=365, value=7, key="checklist_duration")
    
    with col2:
        travel_type = st.selectbox(
            "Travel Type",
            ["leisure", "business", "adventure", "family", "romantic", "backpacking"],
            key="checklist_type"
        )
        checklist_activities = st.multiselect(
            "Planned Activities",
            ["Beach", "Hiking", "City Tour", "Museums", "Nightlife", "Shopping", "Skiing", "Diving", "Wildlife Safari"],
            key="checklist_activities"
        )
    
    if st.button("✨ Generate Checklist", key="generate_checklist"):
        if not checklist_destination:
            st.error("Please enter a destination.")
        else:
            checklist_data = {
                "destination": checklist_destination,
                "duration_days": duration,
                "travel_type": travel_type,
                "activities": checklist_activities
            }
            
            with st.spinner("Generating your personalized checklist..."):
                result = make_api_call("/generate_checklist/", checklist_data)
            
            if result and result.get("checklist"):
                st.subheader("📋 Your Travel Checklist")
                st.markdown(result["checklist"])
                
                # Export checklist
                checklist_text = result["checklist"]
                st.download_button(
                    label="📥 Download Checklist",
                    data=checklist_text,
                    file_name=f"checklist_{checklist_destination}_{travel_type}.md",
                    mime="text/markdown"
                )
            else:
                st.error("Failed to generate checklist. Please try again.")

with tab6:
    st.header("💱 Currency Converter")
    st.markdown("Convert prices between different currencies.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0, key="currency_amount")
        from_currency = st.selectbox("From Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD", "CHF", "CNY"], key="currency_from")
    
    with col2:
        to_currency = st.selectbox("To Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD", "CHF", "CNY"], key="currency_to")
    
    if st.button("🔄 Convert Currency", key="convert_currency"):
        currency_data = {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency
        }
        
        with st.spinner("Converting currency..."):
            result = make_api_call("/convert_currency/", currency_data)
        
        if result:
            st.success(f"**{result.get('formatted', 'Conversion complete')}**")
            st.metric(
                f"{from_currency} to {to_currency}",
                f"{result.get('converted_amount', 0):,.2f} {to_currency}",
                delta=f"Rate: {result.get('exchange_rate', 0):.4f}"
            )
            if result.get("note"):
                st.info(result["note"])

with tab7:
    st.header("⭐ My Favorites")
    st.markdown("View and manage your saved flights and hotels.")
    
    fav_tab1, fav_tab2 = st.tabs(["🛫 Favorite Flights", "🏨 Favorite Hotels"])
    
    with fav_tab1:
        if st.session_state.favorite_flights:
            st.subheader(f"Saved Flights ({len(st.session_state.favorite_flights)})")
            for i, flight in enumerate(st.session_state.favorite_flights):
                with st.expander(f"Flight {i+1}: {flight.get('airline', 'N/A')} - {flight.get('price', 'N/A')}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if flight.get('airline'):
                            st.write(f"**Airline:** {flight.get('airline')}")
                        if flight.get('price'):
                            st.write(f"**Price:** {flight.get('price')}")
                        if flight.get('departure'):
                            st.write(f"**Departure:** {flight.get('departure')}")
                        if flight.get('arrival'):
                            st.write(f"**Arrival:** {flight.get('arrival')}")
                        if flight.get('booking_link'):
                            st.markdown(f"[Book Now]({flight.get('booking_link')})")
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_flight_{i}"):
                            st.session_state.favorite_flights.remove(flight)
                            st.success("Removed from favorites!")
                            st.rerun()
        else:
            st.info("No favorite flights yet. Add flights from the Flight Search tab!")
    
    with fav_tab2:
        if st.session_state.favorite_hotels:
            st.subheader(f"Saved Hotels ({len(st.session_state.favorite_hotels)})")
            for i, hotel in enumerate(st.session_state.favorite_hotels):
                with st.expander(f"Hotel {i+1}: {hotel.get('name', 'N/A')} - {hotel.get('price_per_night', 'N/A')}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if hotel.get('name'):
                            st.write(f"**Name:** {hotel.get('name')}")
                        if hotel.get('price_per_night'):
                            st.write(f"**Price/Night:** {hotel.get('price_per_night')}")
                        if hotel.get('location'):
                            st.write(f"**Location:** {hotel.get('location')}")
                        if hotel.get('rating'):
                            st.write(f"**Rating:** {hotel.get('rating')}")
                        if hotel.get('booking_link'):
                            st.markdown(f"[Book Now]({hotel.get('booking_link')})")
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_hotel_{i}"):
                            st.session_state.favorite_hotels.remove(hotel)
                            st.success("Removed from favorites!")
                            st.rerun()
        else:
            st.info("No favorite hotels yet. Add hotels from the Hotel Search tab!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and AI-powered travel planning")
st.markdown("*Make sure your backend server is running on http://localhost:8000*")
