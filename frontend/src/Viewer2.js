import rome from "./rome_30.jpg"
import rome_ori from "./rome_ori.jpg"
import "bootstrap/dist/css/bootstrap.css"
import React, { Component } from 'react'
import "./viewer.css"
import { getImage } from "./Request"

class Viewer2 extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            lensLength: 40,
            gridXSize: 16,
            gridYSize: 16,
            inputHeight: 500,
            inputWidth: 700,
            keepAspectRatio: true,
            gridSquare: true,
            lockGrid: false,
            gridWidth: 0,
            gridHeight: 0,
            current_selected: [0, 0],
            previewBoxDims: [0, 0]
        }
        this.handleInputChange = this.handleInputChange.bind(this)
        this.renderInputImg = this.renderInputImg.bind(this)
        this.handleInputSubmit = this.handleInputSubmit.bind(this)
        this.handleGridClick = this.handleGridClick.bind(this)
        this.renderOutputImg = this.renderOutputImg.bind(this)
    }

    componentDidMount() {
        // this.imageZoom("myimage", "myresult");
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        if (name == "gridXSize" && this.state.gridSquare) {
            this.setState({
                gridYSize: value
            })
        }
        this.setState({
            [name]: value
        });
    }

    handleInputSubmit() {
        this.renderInputImg();

    }

    handleGridClick(x, y) {
        console.log(x, y)
        this.setState({ current_selected: [x, y] })
        this.renderOutputImg()
    }

    renderInputImg() {
        let img = document.createElement("img")
        img.setAttribute("src", rome)
        img.setAttribute("useMap", "mark")
        img.setAttribute("position", "absolute")
        img.setAttribute("width", this.state.inputWidth + "px")
        img.setAttribute("id", "inputIMG")
        if (!this.state.keepAspectRatio) {
            img.setAttribute("height", this.state.inputHeight + "px")
        }

        let divNode = document.getElementById("inputImg")
        divNode.innerHTML = '';
        divNode.appendChild(img)

        let map = document.createElement("map")
        map.setAttribute("name", "mark")

        const singleWidth = img.offsetWidth / this.state.gridXSize
        const singleHeight = this.state.gridSquare ? singleWidth : img.offsetHeight / this.state.gridYSize

        this.setState({ gridWidth: singleWidth, gridHeight: singleHeight })

        for (let i = 0; i < this.state.gridYSize; i++) {
            for (let j = 0; j < this.state.gridXSize; j++) {
                let area = document.createElement("area")
                let offsetWidth = j * singleWidth
                let offsetHeight = i * singleHeight

                area.setAttribute("shape", "rect");
                area.setAttribute("style", `border: 1px solid red; position: absolute; width: ${singleWidth}px; height: ${singleHeight}px; margin-left: ${offsetWidth}px; margin-top: ${offsetHeight}px`)
                area.onclick = () => this.handleGridClick(i, j);
                map.appendChild(area)
            }
        }

        divNode.appendChild(map)
    }

    renderOutputImg() {
        const originalImg = document.getElementById("inputIMG")
        let originResult = document.getElementById("ori_output")
        let originResizeResult = document.getElementById("oriResize_output")
        let caeResult = document.getElementById("cae_output")
        let cpaResult = document.getElementById("cpa_output")
        const cx = originResult.offsetWidth / this.state.gridWidth;
        const cy = originResult.offsetHeight / this.state.gridHeight;

        originResult.style.backgroundImage = "url('" + rome_ori + "')";
        originResult.style.backgroundSize = (originalImg.width * cx) + "px " + (originalImg.height * cy) + "px";
        originResult.style.backgroundPosition = "-" + (this.state.current_selected[1] * this.state.gridWidth * cx) + "px -" + (this.state.current_selected[0] * this.state.gridHeight * cy) + "px";

        originResizeResult.style.backgroundImage = "url('" + originalImg.src + "')";
        originResizeResult.style.backgroundSize = (originalImg.width * cx) + "px " + (originalImg.height * cy) + "px";
        originResizeResult.style.backgroundPosition = "-" + (this.state.current_selected[1] * this.state.gridWidth * cx) + "px -" + (this.state.current_selected[0] * this.state.gridHeight * cy) + "px";

        this.setState({previewBoxDims: [(originalImg.width * cx*2 ), (originalImg.height*cy*2 )]});
        getImage("decode_cae", this.state)
            .then(response => response.json())
            .then(body => {
                const imgHex = body['data2']
                const hex = Uint8Array.from(Buffer.from(imgHex, 'hex'));
                let nb = new Blob([hex], { type: "image/jpeg" })
                // console.log(imgHex)
                return URL.createObjectURL(nb)
            })
            .then(url => {
                console.log(url)
                caeResult.style.backgroundImage = "url('" + url + "')";
            })
            .catch(err => console.error(err));

        getImage("decode_compressai", this.state)
            .then(response => response.json())
            .then(body => {
                const imgHex = body['data2']
                const hex = Uint8Array.from(Buffer.from(imgHex, 'hex'));
                let nb = new Blob([hex], { type: "image/jpeg" })
                // console.log(imgHex)
                return URL.createObjectURL(nb)
            })
            .then(url => {
                console.log(url)
                cpaResult.style.backgroundImage = "url('" + url + "')";
            })
            .catch(err => console.error(err));
    }


    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col--2">
                        <h3>Image Reconstruction</h3>
                    </div>

                </div>
                <div className="row">
                    <h5>Comparing CAE with CPA</h5>
                </div>

                <ul className="nav nav-pills mb-3" id="pills-tab" role="tablist">
                    <li className="nav-item" role="presentation">
                        <button className="nav-link" id="pills-home-tab" data-bs-toggle="pill" data-bs-target="#pills-home" type="button" role="tab" aria-controls="pills-home" aria-selected="false">Method1</button>
                    </li>
                    <li className="nav-item" role="presentation">
                        <button className="nav-link" id="pills-CAE-tab" data-bs-toggle="pill" data-bs-target="#pills-CAE" type="button" role="tab" aria-controls="pills-CAE" aria-selected="true">CAE</button>
                    </li>
                    <li className="nav-item" role="presentation">
                        <button className="nav-link" id="pills-contact-tab" data-bs-toggle="pill" data-bs-target="#pills-contact" type="button" role="tab" aria-controls="pills-contact" aria-selected="false">Method3</button>
                    </li>
                </ul>
                <div className="row">
                    <hr />
                </div>

                <div className="row">

                    <div className="row">
                        <label className="form-label">Input image dimension:</label>
                        <div className="col">
                            <input className="form-control" aria-describedby="widthHelp" name="inputWidth" value={this.state.inputWidth} onChange={this.handleInputChange}></input>
                            <div id="widthHelp" className="form-text">width in pixel</div>

                        </div>
                        <div className="col">
                            <input className="form-control" aria-describedby="heightHelp" name="inputHeight" value={this.state.inputHeight} disabled={this.state.keepAspectRatio} onChange={this.handleInputChange}></input>
                            <div id="heightHelp" className="form-text">height in pixel</div>
                            <label>
                                Keep aspect ratio:
                            <input
                                    name="keepAspectRatio"
                                    type="checkbox"
                                    checked={this.state.keepAspectRatio}
                                    onChange={this.handleInputChange} />
                            </label>
                        </div>

                    </div>

                    <div className="row">
                        <label className="form-label">Grid dimension:</label>
                        <div className="col">
                            <input className="form-control" aria-describedby="gridXHelp" name="gridXSize" value={this.state.gridXSize} onChange={this.handleInputChange} disabled={this.state.lockGrid}></input>
                            <div id="gridXHelp" className="form-text">Grid X</div>

                        </div>
                        <div className="col">
                            <input className="form-control" aria-describedby="gridYHelp" name="gridYSize" value={this.state.gridYSize} disabled={this.state.gridSquare || this.state.lockGrid} onChange={this.handleInputChange}></input>
                            <div id="gridYHelp" className="form-text">Grid Y</div>
                            <label>
                                Size X == Size Y ?
                            <input
                                    name="gridSquare"
                                    type="checkbox"
                                    checked={this.state.gridSquare}
                                    onChange={this.handleInputChange} />
                            </label>
                        </div>
                    </div>

                    <div className="row">
                        <button className="btn btn-primary" type="submit" onClick={this.handleInputSubmit}>Apply</button>
                    </div>
                </div>

                <div className="row" style={{ marginTop: "30px" }}>
                    <label className="form-label">Current Zoom Level: 24.75x</label>

                    <div className="col">
                        <div className="img-zoom-result" id="ori_output" aria-describedby="ori_outputHelp"></div>
                        <div id="ori_outputHelp" className="form-text">Original 46mb</div>
                    </div>

                    <div className="col">
                        <div className="img-zoom-result" id="oriResize_output" aria-describedby="oriResize_outputHelp"></div>
                        <div id="oriResize_outputHelp" className="form-text">Original (down scaled) 8mb</div>
                    </div>

                    <div className="col">
                        <div className="img-zoom-result" id="cae_output" aria-describedby="cae_outputHelp"></div>
                        <div id="cae_outputHelp" className="form-text">CAE 2mb</div>
                    </div>



                    <div className="col">
                        <div className="img-zoom-result" id="cpa_output" aria-describedby="cpa_outputHelp"></div>
                        <div id="cpa_outputHelp" className="form-text">cpa 22mb</div>
                    </div>

                </div>

                <div id="inputImg" style={{ marginTop: "30px" }}>
                    <img src={rome} alt="usemap" useMap="mark" width="700px" id="inputIMG" />
                    {/* <map name="mark">
                        <area shape="rect" coords="0,0, 250,250" alt="GFG1"
                            style={{ border: "2px solid red", position: "absolute", width: 250, height: 250 }} onClick={() => console.log([1, 1])} />
                        <area shape="rect" coords="250,0, 500,250" alt="GFG2"
                            style={{ border: "2px solid red", position: "absolute", width: 250, height: 250, marginLeft: 250 }} onClick={() => console.log([1, 2])} />
                        <area shape="rect" coords="0,250, 250,500" alt="GFG3"
                            style={{ border: "2px solid red", position: "absolute", width: 250, height: 250, marginTop: 250 }} onClick={() => console.log([2, 1])} />
                        <area shape="rect" coords="250,250, 500,500" alt="GFG4"
                            style={{ border: "2px solid red", position: "absolute", width: 250, height: 250, marginLeft: 250, marginTop: 250 }} onClick={() => console.log([2, 2])} />
                    </map> */}
                </div>
            </div >
        )
    }
}

export default Viewer2
