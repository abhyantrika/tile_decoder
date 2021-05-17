import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Viewer from "./Viewer"
import Viewer2 from "./Viewer2"
import Viewer3 from "./Viewer3"
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    <Viewer2 />
    {/* <Viewer3 img_src="https://upload.wikimedia.org/wikipedia/en/thumb/3/3e/University_of_Maryland_seal.svg/1200px-University_of_Maryland_seal.svg.png" /> */}
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
