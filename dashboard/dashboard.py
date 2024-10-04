import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

sns.set(style='dark')

# ================================= Helper Function yang Dibutuhkan untuk Menyiapkan Berbagai Dataframe ================================= #
# Filter untuk rentang waktu
def create_count_day_df(day_df):
    return day_df.loc[(day_df['dteday'] >= '2011-01-01') & (day_df['dteday'] <= '2012-12-31')]


# Total penyewaan
def create_total_count_df(day_df):
   count_df = day_df.groupby(by='dteday').agg({
      'count_rental': 'sum'
    }).reset_index()
   
   count_df.rename(columns={
        'count_rental': 'count_rental_sum'
    }, inplace=True)
   
   return count_df


# Total registered
def create_total_registered_df(day_df):
   register_df = day_df.groupby(by='dteday').agg({
      'registered': 'sum'
    }).reset_index()
   
   register_df.rename(columns={
        'registered': 'register_sum'
    }, inplace=True)
   
   return register_df


# Total casual
def create_total_casual_df(day_df):
   casual_df = day_df.groupby(by='dteday').agg({
      'casual': 'sum'
    }).reset_index()
   
   casual_df.rename(columns={
        'casual': 'casual_sum'
    }, inplace=True)
   
   return casual_df


# Season
def create_season(day_df):
    # Mengelompokkan berdasarkan musim
    season_df = day_df.groupby('season').agg({
        'count_rental': 'sum'
    }).reset_index()
    
    return season_df

# Weather
def create_weather(day_df):
    # Mengelompokkan berdasarkan cuaca
    weather_df = day_df.groupby('weather').agg({
        'count_rental': 'sum'
    }).reset_index()
    
    return weather_df



# ======================================================== Load Cleaned Data ======================================================== #

file_path = os.path.join(os.path.dirname(__file__), 'day_data_clean.csv')
days_df = pd.read_csv(file_path)

datetime_columns = ['dteday']
days_df.sort_values(by='dteday', inplace=True)
days_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])



# =========================================================== Filter Data =========================================================== #

min_date = days_df['dteday'].min()
max_date = days_df['dteday'].max()

# Membuat sidebar
with st.sidebar:
    st.title('Bike Sharing')

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = days_df[(days_df['dteday'] >= str(start_date)) & 
                (days_df['dteday'] <= str(end_date))]

# Menyiapkan berbagai dataframe
count_day_df = create_count_day_df(main_df)
total_count_df = create_total_count_df(main_df)
register_df = create_total_registered_df(main_df)
casual_df = create_total_casual_df(main_df)
season_df = create_season(main_df)
weather_df = create_weather(main_df)



# ======================================= Melengkapi Dashboard dengan Berbagai Visualisasi Data ======================================= #

# Quick Reports
st.header('Dashboard Bike Sharing')
st.subheader(':rocket: Quick Reports')

col1, col2, col3 = st.columns(3)

with col1:
    total_rental = count_day_df.count_rental.sum()
    st.metric('Total rental', value=total_rental)
with col2:
    total_register = register_df.register_sum.sum()
    st.metric('Total registered', value=total_register)
with col3:
    total_casual = casual_df.casual_sum.sum()
    st.metric('Total casual', value=total_casual)



# Tren Permintaan Penyewaan (semua)
st.subheader('Tren Permintaan Penyewaan (semua)')
plt.figure(figsize=(15, 6))

plt.step(
    total_count_df['dteday'],
    total_count_df['count_rental_sum'], 
    linewidth=2,
    color='#72BCD4'
)

plt.tick_params(axis='y', labelsize=20)
plt.tick_params(axis='x', labelsize=15)
plt.title('Tren Permintaan Penyewaan', fontsize=24)
st.pyplot(plt)



# Tren Permintaan Penyewaan (bulan)
st.subheader('Tren Permintaan Penyewaan (Bulan)')
monthly_data = count_day_df.groupby(by=['year', 'month']).agg({
    'count_rental': 'sum'
}).reset_index()

# Karena jika menggunakan sort maka hasilnya menjadi Apr, Aug, dst. Jadi agar datanya sesuai bulan seperti Jan, Feb, dst kita mendefinisikan ulang.
monthly_data['month'] = pd.Categorical(monthly_data['month'], 
                                        categories=["Jan", "Feb", "Mar", "Apr", 
                                                    "May", "Jun", "Jul", "Aug", 
                                                    "Sep", "Oct", "Nov", "Dec"], ordered=True)

monthly_data.sort_values(by=['year', 'month'], inplace=True)

data_2011 = monthly_data[monthly_data['year'] == 2011]
data_2012 = monthly_data[monthly_data['year'] == 2012]

plt.figure(figsize=(15, 6))

# Line chart 2011
plt.plot(
    data_2011['month'],
    data_2011['count_rental'],
    marker='o', 
    linewidth=2,
    color='#D3D3D3',
    label='2011'
)

# Line chart 2012
plt.plot(
    data_2012['month'],
    data_2012['count_rental'],
    marker='o', 
    linewidth=2,
    color='#72BCD4',
    label='2012'
)

plt.title('Tren Permintaan Penyewaan', loc='center', fontsize=20)
plt.legend(title='Tahun')
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(plt)



# Perbandingan total penyewaan per category_day
st.subheader('Perbandingan Total Penyewaan Hari Kerja dan Hari Libur')
agg_data = count_day_df.groupby(by='category_day').agg({
    'count_rental': 'sum'
}).reset_index()

colors = ['#72BCD4', '#D3D3D3']

plt.figure(figsize=(10, 10))
plt.pie(
    agg_data['count_rental'],
    labels=agg_data['category_day'],
    autopct='%1.1f%%',  # Menampilkan persentase
    startangle=90,
    colors=colors
)
st.pyplot(plt)



# Perbandingan total penyewa register dengan casual
st.subheader('Perbandingan Total Pelanggan Registered dengan Casual')

# Menghitung total untuk pie chart
total_registered = register_df['register_sum'].sum()
total_casual = casual_df['casual_sum'].sum()

data = [total_casual, total_registered]

labels = ['Casual', 'Registered']
colors = ['#D3D3D3', '#72BCD4']

plt.figure(figsize=(10, 10))
plt.pie(
    data, 
    labels=labels, 
    colors=colors, 
    autopct='%1.1f%%', 
    startangle=90
)
st.pyplot(plt)



# Penyewaan Berdasarkan Musim dan Cuaca
st.subheader('Penyewaan Berdasarkan Musim dan Cuaca')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Season
sns.barplot(
    y='count_rental', 
    x='season',
    data=season_df.sort_values(by='season', ascending=False),
    ax=ax[0],
    hue='season',
    legend=False
)

# Mengatur judul, label, dan tick params
ax[0].set_title('Grafik Musim', loc='center', fontsize=50)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].tick_params(axis='y', labelsize=30)

# Weather
sns.barplot(
    y='count_rental', 
    x='weather',
    data=weather_df.sort_values(by='weather', ascending=False),
    ax=ax[1],
    hue='weather',
    legend=False
)

# Mengatur judul, label, dan tick params
ax[1].set_title('Grafik Cuaca', loc='center', fontsize=50)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].tick_params(axis='y', labelsize=30)

st.pyplot(fig)