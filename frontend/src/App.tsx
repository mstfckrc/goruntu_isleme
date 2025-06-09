// import React, { useState, useEffect } from 'react';
// import './App.css';
// import axios from 'axios';

// function App() {

//   const [aktifSekme, setAktifSekme] = useState<'canli' | 'kayitli'>('canli');
//   const [kameraDurumu, setKameraDurumu] = useState<string | null>(null);
//   const [videoURL, setVideoURL] = useState('');
//   const [videoResults, setVideoResults] = useState<Record<string, number> | null>(null);
//   const [loading, setLoading] = useState(false);
//   const [tracking, setTracking] = useState(false);
//   const [sureDoldu, setSureDoldu] = useState(false);
//   const [streamUrl, setStreamUrl] = useState<string>("");
//   const speakingData = res.data || {};
//   // 🔁 Anlık konuşma süresi takibi (her 2 saniyede bir)
//   useEffect(() => {
//     let interval: NodeJS.Timeout;
//     if (tracking) {
//       interval = setInterval(async () => {
//         try {
//           const res = await axios.get("http://localhost:8000/api/live/results");
//           const speakingData = res.data || {};

//           const toplamSure = Object.values(speakingData).reduce((acc, val) => {
//             return acc + Number(val || 0);
//           }, 0);

//           if (toplamSure >= 60) {
//             setSureDoldu(true);
//             setTracking(false);
//           }

//           setVideoResults(speakingData);
//         } catch (err) {
//           console.warn("Canlı analiz sonucu alınamadı:", err);
//         }
//       }, 2000);
//     }

//     return () => clearInterval(interval);
//   }, [tracking]);

//   // 🎥 Stream URL kontrolü (başlatıldığında bir kere set edilir)
//   useEffect(() => {
//     if (tracking) {
//       setStreamUrl(`http://localhost:8000/video_feed?${Date.now()}`);
//     } else {
//       setStreamUrl("");
//     }
//   }, [tracking]);

//   // ▶ Takip başlat
//   const handleCanliBaslat = async () => {
//     try {
//       const response = await axios.post("http://localhost:8000/api/live/start");
//       if (["started", "already_running"].includes(response.data.status)) {
//         setKameraDurumu("✅ Takip başlatıldı.");
//         setVideoResults(null);
//         setSureDoldu(false);
//         setTracking(true);
//       }
//     } catch (error) {
//       setKameraDurumu("❌ Başlatılamadı.");
//     }
//   };

//   const handleCanliDurdur = async () => {
//     try {
//       const res = await axios.post("http://localhost:8000/api/live/stop");
//       if (res.data.status === "stopped") {
//         setKameraDurumu("🛑 Takip durduruldu.");
//         setTracking(false);
//       }
//     } catch (err) {
//       alert("Durdurulamadı.");
//     }
//   };

//   // 🎞️ Kayıtlı video analiz
//   const handleVideoSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     setLoading(true);
//     try {
//       const filename = `video_${Date.now()}`;
//       const res = await axios.post("http://localhost:8000/api/video/analyze", {
//         youtube_url: videoURL,
//         filename: filename
//       });
//       setVideoResults(res.data);
//     } catch (err) {
//       alert("Bir hata oluştu.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const toplamSure = Object.values(speakingData).reduce<number>((acc, val) => {
//   return acc + Number(val);
// }, 0);

// if (toplamSure >= 60) {
//   setSureDoldu(true);
//   setTracking(false);
// }

// setVideoResults(speakingData);

//   return (
//     <div className="App">
//       <header>
//         <h1>🧠 Konuşan Kişi Tanıma Sistemi</h1>
//       </header>

//       <nav>
//         <button onClick={() => setAktifSekme('canli')}>🎥 Canlı Video</button>
//         <button onClick={() => setAktifSekme('kayitli')}>📽️ Kayıtlı Video (YouTube)</button>
//       </nav>

//       <main>
//         {aktifSekme === 'canli' ? (
//           <section>
//             <h2>📡 Canlı Video Üzerinden Konuşan Tanıma</h2>
//             <p>Bu modül canlı kamera akışında konuşan kişiyi tanımlar.</p>
//             <button onClick={handleCanliBaslat}>▶ Tanımayı Başlat</button>
//             <button onClick={handleCanliDurdur} disabled={!tracking}>⏹ Durdur</button>
//             {kameraDurumu && <p>{kameraDurumu}</p>}

//             {tracking && (
//               <img
//                 src={`http://localhost:5000/video_feed?${Date.now()}`} // Cache kırıcı
//                 alt="Kamera Akışı"
//                 style={{ width: '640px', border: '2px solid #ccc', marginTop: '20px' }}
//               />
//             )}

//             {/* ⏱ Süre dolduğunda kullanıcıya uyarı */}
//               {sureDoldu && (
//                   <p style={{ color: "orange", fontWeight: "bold", marginTop: '10px' }}>
//                   ⏱ 60 saniyelik süre doldu. Takibi tekrar başlatabilirsiniz.
//                 </p>
//                 )}


//             <p style={{ fontSize: '14px', marginTop: '10px', color: '#999' }}>
//               ⚠️ Manuel başlatmak istersen: <code>python controller/face/live_speaker_tracker.py</code>
//             </p>
//           </section>
//         ) : (
//           <section>
//             <h2>🎞️ Kayıtlı Video Üzerinden Konuşan Tanıma</h2>
//             <p>YouTube videosu üzerinden konuşan kişiyi tespit edin.</p>
//             <form onSubmit={handleVideoSubmit}>
//               <label>🔗 YouTube Video Linki:</label><br />
//               <input
//                 type="text"
//                 value={videoURL}
//                 onChange={(e) => setVideoURL(e.target.value)}
//                 placeholder="https://youtu.be/..."
//                 style={{ width: '300px' }}
//                 required
//               />
//               <br /><br />
//               <button type="submit">🔍 Analiz Et</button>
//             </form>
//             {loading && <p>⏳ Video analiz ediliyor...</p>}
//           </section>
//         )}

//         {videoResults && (
//           <section>
//             <h3>🧠 Konuşma Süresi Sonuçları:</h3>
//             <table style={{ margin: "0 auto" }}>
//               <thead>
//                 <tr>
//                   <th>Kişi</th>
//                   <th>Süre (saniye)</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {Object.entries(videoResults).map(([name, duration]) => (
//                   <tr key={name}>
//                     <td>{name}</td>
//                     <td>{Math.round(duration)}</td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </section>
//         )}
//       </main>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [aktifSekme, setAktifSekme] = useState<'canli' | 'kayitli' | 'duygu'>('canli');
  const [kameraDurumu, setKameraDurumu] = useState<string | null>(null);
  const [videoURL, setVideoURL] = useState('');
  const [videoResults, setVideoResults] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(false);
  const [tracking, setTracking] = useState(false);
  const [sureDoldu, setSureDoldu] = useState(false);
  const [streamUrl, setStreamUrl] = useState<string>("");
  const [videoFilename, setVideoFilename] = useState('');
  const duyguVideoRef = useRef<HTMLVideoElement>(null);
  const duyguCanvasRef = useRef<HTMLCanvasElement>(null);
  const [emotion, setEmotion] = useState<string | null>(null);

  // 🔁 Konuşma süresi takibi (her 2 saniyede bir)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (tracking) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get("http://localhost:8000/api/live/results");
          const speakingData: Record<string, number> = res.data || {};

          const toplamSure = Object.values(speakingData).reduce<number>((acc, val) => {
            return acc + Number(val);
          }, 0);

          if (toplamSure >= 60) {
            setSureDoldu(true);
            setTracking(false);
          }

          setVideoResults(speakingData);
        } catch (err) {
          console.warn("Canlı analiz sonucu alınamadı:", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [tracking]);

  // 🎥 Kamera yayını başlatıldığında stream URL'ini ayarla
  useEffect(() => {
    if (tracking) {
      setStreamUrl(`http://localhost:8000/video_feed?${Date.now()}`);
    } else {
      setStreamUrl("");
    }
  }, [tracking]);


 const stopEmotionStream = () => {
  const stream = duyguVideoRef.current?.srcObject as MediaStream;
  stream?.getTracks().forEach(track => track.stop());
  setEmotion(null);
};
  // ▶ Takibi başlat
  const handleCanliBaslat = async () => {
    try {
      const response = await axios.post("http://localhost:8000/api/live/start");
      if (["started", "already_running"].includes(response.data.status)) {
        setKameraDurumu("✅ Takip başlatıldı.");
        setVideoResults(null);
        setSureDoldu(false);
        setTracking(true);
      }
    } catch (error) {
      setKameraDurumu("❌ Başlatılamadı.");
    }
  };


  const startEmotionStream = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (duyguVideoRef.current) {
      duyguVideoRef.current.srcObject = stream;
      duyguVideoRef.current.play();
    }
  } catch (err) {
    console.error('Kamera başlatılamadı:', err);
  }
};

const predictFromEmotionStream = () => {
  const canvas = duyguCanvasRef.current;
  const video = duyguVideoRef.current;

  if (!canvas || !video) return;

  const context = canvas.getContext("2d");
  if (!context) return;

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(async (blob) => {
    if (!blob) return;

    const formData = new FormData();
    formData.append("file", blob, "emotion_frame.jpg");

    try {
      const res = await axios.post("http://localhost:8000/api/emotion/", formData);
      setEmotion(res.data.emotion);
    } catch (err) {
      console.error("Duygu tahmini hatası:", err);
    }
  }, "image/jpeg");
};
  // ⏹ Takibi durdur
  const handleCanliDurdur = async () => {
    try {
      const res = await axios.post("http://localhost:8000/api/live/stop");
      if (res.data.status === "stopped") {
        setKameraDurumu("🛑 Takip durduruldu.");
        setTracking(false);
      }
    } catch (err) {
      alert("Durdurulamadı.");
    }
  };

  useEffect(() => {
  let interval: NodeJS.Timeout;
  if (tracking) {
    interval = setInterval(() => {
      captureAndSendEmotion();
    }, 2000);
  }
  return () => clearInterval(interval);
}, [tracking]);

  const captureAndSendEmotion = async () => {
  const video = duyguVideoRef.current;
  const canvas = duyguCanvasRef.current;

  if (video && canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');

      try {
        const res = await fetch('http://localhost:8000/api/emotion/', {
          method: 'POST',
          body: formData,
        });

        const data = await res.json();
        setEmotion(data.emotion);  // 'happy' ya da 'sad'
      } catch (err) {
        console.error('Tahmin hatası:', err);
      }
    }, 'image/jpeg');
  }
};

  // 🎞️ Kayıtlı video analizi
  const handleVideoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const filename = `video_${Date.now()}`;
      const res = await axios.post("http://localhost:8000/api/video/analyze", {
        youtube_url: videoURL,
        filename: filename
      });
      setVideoResults(res.data);
    } catch (err) {
      alert("Bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="App">
    <header>
      <h1>🧠 Konuşan Kişi Tanıma Sistemi</h1>
    </header>

    <nav>
      <button onClick={() => setAktifSekme('canli')}>🎥 Canlı Video</button>
      <button onClick={() => setAktifSekme('kayitli')}>📽️ Kayıtlı Video (YouTube)</button>
      <button onClick={() => setAktifSekme('duygu')}>🧠 Duygu Tanıma</button>
    </nav>

    <main>
      {aktifSekme === 'canli' && (
        <section>
          <h2>📡 Canlı Video Üzerinden Konuşan Tanıma</h2>
          <p>Bu modül canlı kamera akışında konuşan kişiyi tanımlar.</p>
          <button onClick={handleCanliBaslat}>▶ Tanımayı Başlat</button>
          <button onClick={handleCanliDurdur} disabled={!tracking}>⏹ Durdur</button>
          {kameraDurumu && <p>{kameraDurumu}</p>}

          {streamUrl && (
            <img
              src={streamUrl}
              alt="Kamera Akışı"
              style={{ width: '640px', border: '2px solid #ccc', marginTop: '20px' }}
            />
          )}

          {sureDoldu && (
            <p style={{ color: "orange", fontWeight: "bold", marginTop: '10px' }}>
              ⏱ 60 saniyelik süre doldu. Takibi tekrar başlatabilirsiniz.
            </p>
          )}

          <p style={{ fontSize: '14px', marginTop: '10px', color: '#999' }}>
            ⚠️ Manuel başlatmak istersen: <code>python controller/face/live_speaker_tracker.py</code>
          </p>
        </section>
      )}

      {aktifSekme === 'kayitli' && (
        <section>
          <h2>🎞️ Kayıtlı Video Üzerinden Konuşan Tanıma</h2>
          <p>YouTube videosu üzerinden konuşan kişiyi tespit edin.</p>
          <form onSubmit={handleVideoSubmit}>
            <label>🔗 YouTube Video Linki:</label><br />
            <input
              type="text"
              value={videoURL}
              onChange={(e) => setVideoURL(e.target.value)}
              placeholder="https://youtu.be/..."
              style={{ width: '300px' }}
              required
            />
            <br /><br />
            <label>💾 Video Dosya Adı:</label><br />
            <input
              type="text"
              value={videoFilename}
              onChange={(e) => setVideoFilename(e.target.value)}
              placeholder="ornek_video.mp4"
              style={{ width: '300px' }}
              required
            />
            <br /><br />
            <button type="submit">🔍 Analiz Et</button>
          </form>
          {loading && <p>⏳ Video analiz ediliyor...</p>}
        </section>
      )}

      {aktifSekme === 'duygu' && (
        <section>
          <h3>🧠 Kamera ile Duygu Tanıma</h3>
          <video ref={duyguVideoRef} autoPlay muted style={{ width: 400 }} />
          <canvas ref={duyguCanvasRef} style={{ display: 'none' }} />

          <div style={{ marginTop: 10 }}>
            <button onClick={startEmotionStream}>📷 Kamerayı Aç (Duygu)</button>
            <button onClick={captureAndSendEmotion}>🎯 Duygu Tahmini Yap</button>
            <button onClick={stopEmotionStream} style={{ marginLeft: 10 }}>
              🔒 Kamerayı Kapat (Duygu)
            </button>
          </div>

          {emotion && (
            <p style={{ marginTop: '10px', fontWeight: 'bold', fontSize: '18px' }}>
              Tahmin Edilen Duygu: <span style={{ color: emotion === 'happy' ? 'green' : 'red' }}>{emotion}</span>
            </p>
          )}
        </section>
      )}

      {videoResults && (
        <section>
          <h3>🧠 Konuşma Süresi Sonuçları:</h3>
          <table style={{ margin: "0 auto" }}>
            <thead>
              <tr>
                <th>Kişi</th>
                <th>Süre (saniye)</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(videoResults).map(([name, duration]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{Math.round(duration)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  </div>
);
}
export default App;