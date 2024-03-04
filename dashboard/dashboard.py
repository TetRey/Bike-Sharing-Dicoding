import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="Capital Bikeshare: Bike-sharing Dashboard",
                   page_icon="bike:",
                   layout="wide")

sns.set_theme(style="dark")
plt.style.use('dark_background')
background_color = '#0E1117'
plt.rcParams['axes.facecolor'] = background_color
plt.rcParams['figure.facecolor'] = background_color

# Fungsi untuk menerima dan mengelola data
def create_monthly_rent(data):
    grouped_by_year_month = data.groupby(['yr', 'mnth'])
    total_rentals_per_month = grouped_by_year_month['cnt'].sum()
    monthly_rent_data = total_rentals_per_month.unstack('yr')
    return monthly_rent_data

def create_hourly_working_day(data):
    grouped_workingday_data = data.groupby(['workingday', 'hr'])['cnt'].sum()
    hourly_working_day_data = grouped_workingday_data.unstack('workingday')
    return hourly_working_day_data

def create_season_counts(data):
    season_counts = data.groupby('season')['cnt'].sum().reset_index()
    return season_counts

def create_weather_counts(data):
    weather_counts = data.groupby(by='weathersit').agg({
        'cnt': 'sum'
    })
    return weather_counts

def create_day_type_counts(data):
    workingday_data = data[data['workingday'] == 1]
    non_workingday_data = data[data['workingday'] == 0]
    workingday_total = workingday_data[['casual', 'registered', 'cnt']].sum()
    non_workingday_total = non_workingday_data[['casual', 'registered', 'cnt']].sum()
    workingday_values = [workingday_total['casual'], workingday_total['registered'], workingday_total['cnt']]
    non_workingday_values = [non_workingday_total['casual'], non_workingday_total['registered'], non_workingday_total['cnt']]
    return workingday_values, non_workingday_values 

def create_rfm_analysis(data):
    rfm_analysis = data.groupby(by="weekday", as_index=False).agg({
    "dteday": "max", # Tanggal akhir order
    "instant": "nunique", # Menghitung kuantitas order
    "cnt": "sum" # Menghitung jumlah penyewa
    })

    rfm_analysis.columns = ["weekday", "max_order_timestamp", "frequency", "monetary"]

    rfm_analysis["max_order_timestamp"] = rfm_analysis["max_order_timestamp"].dt.date
    recent_date = data["dteday"].dt.date.max()
    rfm_analysis["recency"] = rfm_analysis["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_analysis.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_analysis

# Mengimport data
day_df = pd.read_csv('day.csv')
hour_df = pd.read_csv('hour.csv')

# Mengkonversi data type
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Membuat sidebar untuk memfilter tanggal
min_date = pd.to_datetime(day_df['dteday']).dt.date.min()
max_date = pd.to_datetime(day_df['dteday']).dt.date.max()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png")
    start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value= min_date,
            max_value= max_date,
            value=[min_date, max_date]
        )
    st.text('*Rentang waktu minimal 1 tahun')
    st.caption("Copyright (c) Reyhan Eldwin Maulana 2024")

main_day_df = day_df[(day_df['dteday'] >= str(start_date)) & 
                (day_df['dteday'] <= str(end_date))]



monthly_rent_data = create_monthly_rent(main_day_df)
hourly_working_day_data = create_hourly_working_day(hour_df)
season_counts = create_season_counts(day_df)
weather_counts = create_weather_counts(main_day_df)
workingday_values, non_workingday_values= create_day_type_counts(main_day_df)
rfm_analysis = create_rfm_analysis(main_day_df)

st.title("Bike Sharing Dashboard :bike:")

# Memvisualisasikan data dashboard 1
st.subheader("Trend penyewaan sepeda pada tahun 2011 dan 2012")
col1, col2, col3 = st.columns(3)
with col1 :
    total_2011 = monthly_rent_data[0].sum()
    st.metric("Total Rental in 2011", value=f'{total_2011:,}')
with col2 :
    total_2012 = monthly_rent_data[1].sum()
    st.metric("Total Rental in 2012", value=f'{total_2012:,}')
with col3 : 
    total_rent_year = monthly_rent_data[0].sum()+monthly_rent_data[1].sum()
    st.metric("Total Rental", value=f'{total_rent_year:,}')

plt.title('Rental Amount Based on Year')
plt.figure(figsize=(15, 5))
for i, year in enumerate(monthly_rent_data.columns):
    legend_label = f'Tahun {year+2011}' if year == 0 else f'Tahun {year + 2011}'
    color = 'skyblue' if i == 0 else 'red'  # Choose color based on index
    plt.plot(monthly_rent_data.index, monthly_rent_data[year], label=legend_label, marker='o', linestyle='-', color=color)
plt.title('Rental Amount Based on Year')
plt.xlabel('Bulan')
plt.ylabel('Jumlah Penyewaan Sepeda')
plt.grid(True)
plt.legend()
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
st.pyplot(plt)
plt.clf()

# Memvisualisasikan data dashboard 2
st.subheader("Rental Amount Based on Weather")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rent on Sunny", value=f'{weather_counts.iloc[0, 0]:,}')
with col2:
    st.metric("Total Rent on Cloudy", value=f'{weather_counts.iloc[1, 0]:,}')
with col3:
    st.metric("Total Rent on Rain", value=f'{weather_counts.iloc[2, 0]:,}')

plt.figure(figsize=(8, 3)) 
sns.barplot(
    x='weathersit',
    y='cnt',
    data=weather_counts,
    palette='dark:salmon_r',
    width=.35)
plt.xticks(ticks=[0, 1, 2], labels=['Cerah/Sedikit Berawan', 'Mendung/Berkabut', 'Salju/Hujan'])
plt.title('Jumlah Penyewa Sepeda berdasarkan Kondisi Cuaca')
plt.xlabel('Cuaca')
plt.ylabel('Jumlah Penyewa Sepeda')
plt.tight_layout() 
plot_image = plt.gcf()  
st.pyplot(plot_image)
plt.clf()  

# Memvisualisasikan data dashboard 3
st.subheader("Workingday vs Holiday Based on User Status")
col1, col2 = st.columns(2)
with col1:
    total_casual = workingday_values[0] + non_workingday_values[0]  
    st.metric("Total Casual Rent", value=f'{total_casual:,}')
with col2:
    total_registered = workingday_values[1] + non_workingday_values[1]  
    st.metric("Total Registered Rent", value=f'{total_registered:,}')
categories = ['Casual', 'Registered', 'Total Penyewa']
bar_width = 0.35
index = range(len(categories))

plt.figure(figsize=(8, 3))  
plt.bar(index, workingday_values, bar_width, label='Hari Kerja', color='#7fbf7f')
plt.bar([i + bar_width for i in index], non_workingday_values, bar_width, label='Hari Libur', color='#7f7fff')

plt.xlabel('Kategori')
plt.ylabel('Jumlah Penyewa')
plt.title('Jumlah Penyewa Berdasarkan Kategori dan Hari')
plt.xticks([i + bar_width / 2 for i in index], categories)
plt.legend()
st.pyplot(plt)
plt.clf()


# Memvisualisasikan data dashboard 4
st.subheader("Rental Amount Based on Hour")
col1, col2 = st.columns(2)
with col1:
    rush_hour = '5:00 PM'  # Example time during peak traffic
    st.metric("High Traffic", value=f'{rush_hour}')

with col2:
    off_peak_hour = '2:00 AM'  # Example time during off-peak traffic
    st.metric("Low Traffic", value=f'{off_peak_hour}')
workingday_data = hourly_working_day_data[1]
plt.figure(figsize=(15, 4))
plt.plot(workingday_data.index, workingday_data.values, marker='o', linestyle='-',color='orange')
plt.title('Jumlah Penyewaan Sepeda per Jam pada Hari Kerja')
plt.xlabel('Jam (hr)')
plt.ylabel('Jumlah Penyewaan Sepeda')
plt.grid(True)
plt.xticks(range(24))
st.pyplot(plt)

# Memvisualisasikan data dashboard 5
st.subheader('Rental Amount Based on Season')
plt.figure(figsize=(8, 2))
plt.xlabel("")
plt.ylabel("")
explode = (0, 0, 0.1, 0)
color_palette = sns.color_palette("dark:#5A9_r")
patches, texts, autotexts = plt.pie(season_counts['cnt'], labels=['Spring', 'Summer', 'Fall', 'Winter'], autopct='%1.1f%%', explode=explode, colors=color_palette, startangle=140)
for text in texts + autotexts:
    text.set_fontsize(5)
    text.set_color('white')  
for i, text in enumerate(autotexts):
    percentage = float(text.get_text().strip('%'))
    count = season_counts['cnt'][i]
    text.set_text(f"{percentage:.1f}%\n{count}")    
plt.title('Perbandingan Jumlah Penyewa Sepeda Berdasarkan Musim', fontsize=7)  
st.pyplot(plt)

# Memvisualisasikan data dashboard 6
st.subheader("RFM Analysis")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="weekday", data=rfm_analysis.sort_values(by="recency", ascending=True).head(5), palette=colors, hue="weekday", legend=False, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Berdasarkan Kekinian (Weekdays)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="frequency", x="weekday", data=rfm_analysis.sort_values(by="frequency", ascending=False).head(5), palette=colors, hue="weekday", legend=False, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Berdasarkan Frekuensi", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="weekday", data=rfm_analysis.sort_values(by="monetary", ascending=False).head(5), palette=colors, hue="weekday", legend=False, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("Berdasarkan Moneter", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Pelanggan Terbaik Berdasarkan Parameter RFM (Weekday)", fontsize=20)
st.pyplot(plt)
