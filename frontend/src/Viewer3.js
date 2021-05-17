import React, { Component } from 'react'
import rome from "./rome_30.jpg"
import rome_ori from "./rome_ori.jpg"
import "bootstrap/dist/css/bootstrap.css"
import "./view3.css"

class Zoomer extends Component {
    constructor(props) {
        super(props)
        this.img_ele = null
        this.x_img_ele = null
        this.y_img_ele = null

        this.hasTouch = this.hasTouch.bind(this)
        this.zoom = this.zoom.bind(this)
        this.start_drag = this.start_drag.bind(this)
        this.stop_drag = this.stop_drag.bind(this)
        this.while_drag = this.while_drag.bind(this)
    }
    componentDidMount() {
        var
            event_start = 'mousedown',
            event_move = 'mousemove',
            event_end = 'mouseup';
        console.log(event_start + "|" + event_move + "|" + event_end);

        document.getElementById('zoomout').addEventListener('click', () => {
            this.zoom(0.5);
        });
        document.getElementById('zoomin').addEventListener('click', () => {
            this.zoom(1.5);
        });

        document.getElementById('drag-img').addEventListener(event_start, this.start_drag);
        document.getElementById('container').addEventListener(event_move, this.while_drag);
        document.getElementById('container').addEventListener(event_end, this.stop_drag);
    }
    hasTouch() {
        return 'ontouchstart' in document.documentElement;
    }
    zoom(zoomincrement) {
        this.img_ele = document.getElementById('drag-img');
        var pre_width = this.img_ele.getBoundingClientRect().width,
            pre_height = this.img_ele.getBoundingClientRect().height;
        this.img_ele.style.width = (pre_width * zoomincrement) + 'px';
        this.img_ele.style.height = (pre_height * zoomincrement) + 'px';
        this.img_ele = null;

        let r1 = document.getElementById('drag-img-1');
        var pre_width = r1.getBoundingClientRect().width,
            pre_height = r1.getBoundingClientRect().height;
        r1.style.width = (pre_width * zoomincrement) + 'px';
        r1.style.height = (pre_height * zoomincrement) + 'px';

        let r2 = document.getElementById('drag-img-2');
        var pre_width = r2.getBoundingClientRect().width,
            pre_height = r2.getBoundingClientRect().height;
        r2.style.width = (pre_width * zoomincrement) + 'px';
        r2.style.height = (pre_height * zoomincrement) + 'px';

        let r3 = document.getElementById('drag-img-3');
        var pre_width = r3.getBoundingClientRect().width,
            pre_height = r3.getBoundingClientRect().height;
        r3.style.width = (pre_width * zoomincrement) + 'px';
        r3.style.height = (pre_height * zoomincrement) + 'px';
    }

    start_drag(event) {
        event.preventDefault()
        this.img_ele = document.getElementById('drag-img');
        var x_cursor = event.clientX,
            y_cursor = event.clientY;
        this.x_img_ele = x_cursor - this.img_ele.offsetLeft;
        this.y_img_ele = y_cursor - this.img_ele.offsetTop;
        console.log("start drag");
    }

    stop_drag() {
        this.img_ele = null;
        console.log("stop drag");
    }
    while_drag(event) {
        event.preventDefault()
        var x_cursor = event.clientX,
            y_cursor = event.clientY;
        if (this.img_ele !== null) {
            this.img_ele.style.left = (x_cursor - this.x_img_ele) + 'px';
            this.img_ele.style.top = (y_cursor - this.y_img_ele) + 'px';
            // console.log('dragging > img_left:' + this.img_ele.style.left + ' | img_top: ' + this.img_ele.style.top);

            let r1 = document.getElementById('drag-img-1');
            r1.style.left = (x_cursor - this.x_img_ele) + 'px';
            r1.style.top = (y_cursor - this.y_img_ele) + 'px';

            let r2 = document.getElementById('drag-img-2');
            r2.style.left = (x_cursor - this.x_img_ele) + 'px';
            r2.style.top = (y_cursor - this.y_img_ele) + 'px';

            let r3 = document.getElementById('drag-img-3');
            r3.style.left = (x_cursor - this.x_img_ele) + 'px';
            r3.style.top = (y_cursor - this.y_img_ele) + 'px';


        }
    }

    render() {
        return (
            <div className="row">
                <div className="col">
                    <div id="container">
                        <img className="dragImg" id="drag-img" src={this.props.img_src} />
                    </div>
                    <input type="button" id="zoomout" className="button" value="Zoom out" />
                    <input type="button" id="zoomin" className="button" value="Zoom in" />
                </div>
                <div className="col">
                    <div id="container">
                        <img className="dragImg" id="drag-img-1" src={this.props.img_src_1} />
                    </div>

                </div>

                <div className="col">
                    <div id="container">
                        <img className="dragImg" id="drag-img-2" src={this.props.img_src_2} />
                    </div>

                </div>

                <div className="col">
                    <div id="container">
                        <img className="dragImg" id="drag-img-3" src={this.props.img_src_3} />
                    </div>

                </div>
            </div>
        )
    }
}
export default Zoomer