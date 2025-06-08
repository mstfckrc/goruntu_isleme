import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import scipy.fftpack

def load_audio_data(audio_file):
    audio = AudioSegment.from_wav(audio_file)  
    samples = np.array(audio.get_array_of_samples()) 
    return samples, audio.frame_rate  

def plot_time_domain(audio_data):
    plt.subplot(2, 1, 1)  # 2 satır 1 sütunlu gridin 1. alt grafiği
    plt.plot(audio_data)
    plt.title("Zaman Domaini - Ses Dalga Formu")
    plt.xlabel("Zaman (örnekler)")
    plt.ylabel("Genlik")
    plt.grid(True)

def plot_frequency_domain(audio_data, sample_rate):
    n = len(audio_data)
    freqs = np.fft.fftfreq(n, 1/sample_rate)
    fft_values = np.abs(np.fft.fft(audio_data))

    plt.subplot(2, 1, 2)  # 2 satır 1 sütunlu gridin 2. alt grafiği
    plt.plot(freqs[:n//2], fft_values[:n//2])  
    plt.title("Frekans Domaini - Spektrum")
    plt.xlabel("Frekans (Hz)")
    plt.ylabel("Genlik")
    plt.grid(True)

# Ana fonksiyon
def main():
    
    audio_file = "data/records/Doğa/Doğa_1.wav"  
    audio_data, sample_rate = load_audio_data(audio_file)

   
    plt.figure(figsize=(12, 8)) 
    plot_time_domain(audio_data)
    plot_frequency_domain(audio_data, sample_rate)

    plt.tight_layout()  
    plt.show()

if __name__ == "__main__":
    main()
