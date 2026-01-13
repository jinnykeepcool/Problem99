import streamlit as st

st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to bottom, #121212, #000000); /* Dark gradient background */
        color: #FFFFFF; /* White text */
    }
    .sidebar .sidebar-content {
        background: #000000; /* Black sidebar */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1DB954; /* Spotify green for headings */
    }
    p, .stText {
        color: #B3B3B3; /* Light grey for regular text */
    }
    .stButton>button {
        background-color: transparent; /* Transparent buttons */
        color: #1DB954; /* Spotify green text */
        border: 2px solid #1DB954; /* Green border */
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: rgba(29, 185, 84, 0.2); /* Subtle green background on hover */
        color: white; /* White text on hover */
        border-color: white; /* White border on hover */
    }
    .stTextInput>div>div>input {
        background-color: #282828; /* Darker input fields */
        color: #FFFFFF;
        border: 1px solid #535353;
        border-radius: 5px;
    }
    .stFileUploader>div>div>div>button {
        background-color: #535353;
        color: white;
        border-radius: 5px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Song Class ---
class Song:
    def __init__(self, title, artist, audio_data=None):
        self.title = title
        self.artist = artist
        self.audio_data = audio_data
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist, audio_data=None):
        new_song = Song(title, artist, audio_data)
        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            current = self.head
            while current.next_song:
                current = current.next_song
            current.next_song = new_song
        self.length += 1
        st.success(f"Added: {new_song}")

    def display_playlist(self):
        if self.head is None:
            return []

        playlist_songs = []
        current = self.head
        count = 1
        while current:
            playlist_songs.append(f"{count}. {current.title} by {current.artist}")
            current = current.next_song
            count += 1
        return playlist_songs

    def play_current_song(self):
        if self.current_song:
            st.markdown(f"**Now playing:** <span style='color:#1DB954;'>{self.current_song}</span>", unsafe_allow_html=True)
            if self.current_song.audio_data:
                st.audio(self.current_song.audio_data, format='audio/wav')
            else:
                st.info("No audio data available for this song.")
        else:
            st.warning("Playlist is empty or no song is selected to play.")

    def next_song(self):
        if self.current_song and self.current_song.next_song:
            self.current_song = self.current_song.next_song
        elif self.current_song and not self.current_song.next_song:
            st.warning("End of playlist. No next song.")
        else:
            st.warning("Playlist is empty.")

    def prev_song(self):
        if self.head is None or self.current_song is None:
            st.warning("Playlist is empty or no song is selected.")
            return
        if self.current_song == self.head:
            st.warning("Already at the beginning of the playlist.")
            return

        current = self.head
        prev = None
        while current.next_song != self.current_song:
            prev = current
            current = current.next_song
        self.current_song = current

    def get_length(self):
        return self.length

    def delete_song(self, title):
        if self.head is None:
            st.error(f"Cannot delete '{title}'. Playlist is empty.")
            return

        # Special case: Deleting the head
        if self.head.title == title:
            if self.current_song == self.head:
                # If current song is head and there's a next song, move to next
                # Else if there's no next song, or no other songs, current song becomes None
                self.current_song = self.head.next_song if self.head.next_song else None
            self.head = self.head.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
            return

        current = self.head
        prev = None
        while current and current.title != title:
            prev = current
            current = current.next_song

        if current:
            # If the song to delete is the current song
            if self.current_song == current:
                if current.next_song: # If there's a next song, move current to next
                    self.current_song = current.next_song
                elif prev: # If no next song but there was a previous, move current to previous
                    self.current_song = prev
                else: # If it's the only song left and being deleted, current becomes None
                    self.current_song = None

            prev.next_song = current.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
        else:
            st.error(f"Song '{title}' not found in the playlist.")


st.title("🎶 Spotify-like Music Player")

if 'playlist' not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

# --- Sidebar for Add/Delete Song ---
st.sidebar.header("Manage Your Music")

with st.sidebar:
    st.markdown("---")
    st.subheader("Add New Song")
    new_title = st.text_input("Title", key="add_title")
    new_artist = st.text_input("Artist", key="add_artist")
    uploaded_audio = st.file_uploader("Upload Audio File", type=['wav', 'mp3'], key="add_audio")

    if st.button("Add Song to Playlist", key="add_song_btn"):
        if new_title and new_artist:
            audio_data_bytes = None
            if uploaded_audio is not None:
                audio_data_bytes = uploaded_audio.read()
            st.session_state.playlist.add_song(new_title, new_artist, audio_data_bytes)
        else:
            st.warning("Please enter both title and artist.")

    st.markdown("---")
    st.subheader("Delete Song")
    delete_title = st.text_input("Song Title to Delete", key="delete_title")
    if st.button("Delete Song", key="delete_song_btn"):
        if delete_title:
            st.session_state.playlist.delete_song(delete_title)
        else:
            st.warning("Please enter a song title to delete.")

# --- Main Content Area ---
st.markdown("<br>", unsafe_allow_html=True) # Add some space

# Now Playing Section
st.subheader("🎶 Now Playing")
st.container(border=True).markdown(f"**Current Song:** {st.session_state.playlist.current_song if st.session_state.playlist.current_song else 'No song playing'}")

# Playback controls
col1, col2, col3 = st.columns([1,2,1]) # Wider middle column for play button
command = 0
with col1:
    if st.button("⏪ Previous"):
        command = 1

with col2:
    if st.button("▶️ Play Current"):
        command = 2

with col3:
    if st.button("⏩ Next"):
        command = 3

# Execute playback command
match command:
    case 1:
        st.session_state.playlist.prev_song()
        st.session_state.playlist.play_current_song()
    case 2:
        st.session_state.playlist.play_current_song()
    case 3:
        st.session_state.playlist.next_song()
        st.session_state.playlist.play_current_song()
    case _:
        # If no button pressed (e.g., initial load, or after adding/deleting), display current song if one exists
        if st.session_state.playlist.current_song:
            st.session_state.playlist.play_current_song()

st.markdown("<br>", unsafe_allow_html=True) # Add some space

# Your Current Playlist Section
st.subheader("🎵 Your Playlist")
playlist_content = st.session_state.playlist.display_playlist()
if playlist_content:
    playlist_container = st.container(border=True)
    for song_str in playlist_content:
        playlist_container.write(song_str)
else:
    st.info("Playlist is empty. Add some songs from the sidebar!")

st.markdown("---")
st.write(f"Total songs in playlist: {st.session_state.playlist.get_length()} song(s)")
