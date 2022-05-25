import './App.css';
import * as React from 'react';
import Slider from '@mui/material/Slider';
import Box from '@mui/material/Box';
import NumericInput from 'react-numeric-input';
import 'react-h5-audio-player/lib/styles.css';
import song from './sounds/results.wav';


import Button from '@mui/material/Button';
import SendIcon from '@mui/icons-material/Send';

var SliderTiempo_value = 16;
var SliderAtenuacion_value = 64;
var transition_time = 10;
var song1 = ""
var song2 = ""

function changeSong1(value){
  console.log(value)
  song1 = value;
}

function changeSong2(value){
  song2 = value;
}

function SliderTiempo(value) {
  SliderTiempo_value = value;
}

function SliderAtenuacion(value) {
  SliderAtenuacion_value = value;
}

function NumericInputChange(value) {
  transition_time = value;
}



// var songs = [
//   {
//     "id": 1,
//     "path": "daniela_andrade",
//     "title": "Crazy Daniela Andrade",
//     "image_path": "https://i.scdn.co/image/ab67616d00001e0229455064ffc25216a8a576b2",
//   },
//   {
//     "id": 2,
//     "path": "Gnarls-Barkley-Crazy_cortado",
//     "title": "Crazy Gnarls Barkley",
//     "image_path": "https://m.media-amazon.com/images/I/81mWl+Yr5nL._SS500_.jpg",
//   },
//   {
//     "id": 2,
//     "path": "starwars",
//     "title": "Star Wars",
//     "image_path": "https://images.unsplash.com/photo-1618336753974-aae8e04506aa?crop=entropy&cs=tinysrgb&fm=jpg&ixlib=rb-1.2.1&q=80&raw_url=true&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170",
//   },
//   {
//     "id": 4,
//     "path": "goingup60_mono",
//     "title": "Going Up",
//     "image_path": "https://images.unsplash.com/photo-1557177324-56c542165309?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80",
//   }

// ]


// function Send_data(){
//   console.log("sending data: {song1: " + song1 + ", song2: " + song2 + ", SliderTiempo: " + SliderTiempo_value.toString() + ", SliderAtenuacion: " + SliderAtenuacion_value.toString() + ", NumericInputChange: " +  transition_time.toString() + "}");
//   fetch(
//     "http://localhost:8000/mix?song_1=" + song1 + "&song_2=" + song2 + "&f_second=" + SliderTiempo_value.toString() + "&time_to_switch=" + transition_time.toString() + "&attenuation=" + SliderAtenuacion_value.toString())
//                 .then((res) => res.json())
//                 .then((json) => {
//                     console.log(json);
//                     // my_Audio();
//                     });
// }




// function my_Audio() {
//   document.getElementById("mp4_src").src =
// "results2.wav"; 

//   document.getElementById("my_Audio").load();
// }

function App() {
  const [path, setpath] = React.useState(song);
  const [songs, setsongs] = React.useState([]);

  

  React.useEffect(() => {
    setpath(song);
    fetch(
      "http://localhost:8000/songs")
                  .then((res) => res.json())
                  .then((json) => {
                      setsongs(json);
                      });
  }, []);

  var rows = [];
for (const song in songs) {
    rows.push(
      <a className="card" onClick={() => changeSong1(songs[song].path)}>
            <div className="card_background" style={{ backgroundImage: "url(" + songs[song].image_path + ")"}}>
</div>
            <div className="card_content">
              <p className="card_category">{songs[song].bpm} BPMs</p>
              <h3 className="card_heading">{songs[song].title}</h3>
            </div>
          </a>
    );
}

var rows2 = [];
for (const song in songs) {
  rows2.push(
      <a className="card" onClick={() => changeSong2(songs[song].path)}>
            <div className="card_background" style={{ backgroundImage: "url(" + songs[song].image_path + ")"}}>
</div>
            <div className="card_content">
              <p className="card_category">{songs[song].bpm} BPMs</p>
              <h3 className="card_heading">{songs[song].title}</h3>
            </div>
          </a>
    );
}

  const Send_datados = () => {
    console.log("sending data: {song1: " + song1 + ", song2: " + song2 + ", SliderTiempo: " + SliderTiempo_value.toString() + ", SliderAtenuacion: " + SliderAtenuacion_value.toString() + ", NumericInputChange: " +  transition_time.toString() + "}");
    fetch(
      "http://localhost:8000/mix?song_1=" + song1 + "&song_2=" + song2 + "&f_second=" + transition_time.toString() + "&time_to_switch=" + SliderTiempo_value.toString() + "&attenuation=" + SliderAtenuacion_value.toString())
                  .then((res) => res.json())
                  .then((json) => {
                      console.log(json);
                      setpath(song); 
                      });
  }

  return (
    <div>

    <section className="hero-section">
      
      <div className="grid">

        {/****************** Listas de canciones *******************/}
        <div  style={{display:"flex", justifyContent: "center", alignItems: "center", color: "white", fontSize: "30px"}}>
          <h1>Sound Mixer</h1>
        </div>
        <div  style={{display:"flex", justifyContent: "center", alignItems: "center", color: "gray", fontSize: "30px"}}>
          <span>Seleccione 2 canciones a mezclar y los parámetros necesarios para la reproducción.</span>
        </div>
        <h2>Primera canción</h2>

        <tbody className="card-grid">{rows}</tbody>
          
        <h2>Segunda canción</h2>

        <tbody className="card-grid">{rows2}</tbody>

        {/****************** Sector configuración *******************/}
        <div className="card-grid">
        </div>
        <div style={{display:"flex", justifyContent: "center", alignItems: "center"}}>
          <Box width={500}>
            <div style={{display:"flex", justifyContent: "center", alignItems: "center", color: "white", fontSize: "20px"}}>
              <h2 style={{marginBottom: "40px", marginTop: "40px"}}>Selección de parámetros</h2>
            </div>
            <h2>Tiempo para el cambio de canción (segundos)</h2>
            <Slider defaultValue={16} aria-label="Default" valueLabelDisplay="auto" getAriaValueText={SliderTiempo} marks min={1}
          max={32}/>
            <h2>Atenuación en el cambio (veces)</h2>
            <Slider defaultValue={64} aria-label="Default" valueLabelDisplay="auto" step={1} marks min={4}
          max={128} getAriaValueText={SliderAtenuacion}/>
            <h2 style={{marginBottom: "20px"}}>Segundo donde comienza a ocurrir el cambio</h2>
            <div style={{display:"flex", justifyContent: "center", alignItems: "center"}}>
            <NumericInput min={0} max={100} value={10} style={{
            input: {
              height: "30px"
              }
            }} onChange={NumericInputChange}/>
            </div>
            <br></br>
            <div style={{justifyContent:"center", display: "flex"}}>
              <Button style={{marginTop: "20px", justifyContent: 'center', width: "30%", height: "40px"}} variant="contained" endIcon={<SendIcon />} onClick={Send_datados}>
                Enviar
              </Button>
            </div>
            <div style={{justifyContent:"center", display: "flex", color: "white", fontSize: "20px"}}>
              <h1 style={{marginTop: "30px"}}>Audio resultante</h1>
            </div>
            <div style={{justifyContent:"center", display: "flex"}}>
              <audio
              id="my_Audio"
              style={{width: "100%", marginTop: "20px"}}
              controls
              src={path}>
                <source id="mp4_src" src={song} type="audio/mp3">
                </source>
              </audio>
            </div>
          </Box>
        </div>
      </div>
    </section>
  </div>
  );
}

export default App;
