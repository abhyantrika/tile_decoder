const backendurl = "http://localhost:8000/"

export function getImage(route_url, coords) {
    return fetch(backendurl + route_url + "?" + new URLSearchParams({
        x: coords[0],
        y: coords[1],
    })
    )
}