import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write(
    """
    **Choose the fruits you want in your custom smoothie!**
    """
)

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Create a Snowflake session
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")

# Fetch fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).to_pandas()
    st.dataframe(data=my_dataframe, use_container_width=True)
except Exception as e:
    st.error(f"Error fetching data: {e}")

# Convert DataFrame to a list for the multiselect widget
fruit_options = my_dataframe['fruit_name'].tolist() if 'my_dataframe' in locals() else []

ingredients_list = st.multiselect(
    'Choose up to five ingredients:',
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Use parameterized query to prevent SQL injection
    my_insert_stmt = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (%s, %s)"

    time_to_insert = st.button('Submit order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
            st.success('Your smoothie is ordered!', icon=" ✅")
        except Exception as e:
            st.error(f"Error inserting data: {e}")
