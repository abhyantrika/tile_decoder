const backendurl = "http://localhost:8000/"

export function getImage(route_url, state ) {
    const {current_selected, gridXSize, gridYSize, previewBoxDims} = state;
    return fetch(backendurl + route_url + "?" + new URLSearchParams({
        x: current_selected[0],
        y: current_selected[1],
        gridXSize,
        gridYSize,
        totalWidth: previewBoxDims[0],
        totalHeight: previewBoxDims[1]
    })
    );
}