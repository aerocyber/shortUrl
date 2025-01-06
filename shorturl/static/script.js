const BASE_URL = location.href;

console.log(BASE_URL);

async function shortenBtnClicked() {
    const endpoint_url = BASE_URL + '/shorten';
    const url = document.getElementById('long-url').value;
    if (url === '' || url === null) {
        document.getElementById('err-text').innerHTML = `Encountered an error: No URL entered`;
        return;
    }
    document.getElementById('err-text').innerHTML = '';
    document.getElementById('success-text').innerHTML = '';
    try {
        var resp = await fetch(endpoint_url, {
            method: "POST",
            body: JSON.stringify({'long-url': url}),
            headers: {"Access-Control-Allow-Origin": "*"}
        });
        if(!resp.ok) {
            document.getElementById('error').classList.toggle('hide');
            document.getElementById('err-text').innerHTML = `Encountered an error: ${resp.text}`;
        } else {
            var shortcode = await resp.text();
            document.getElementById('success').classList.toggle('hide');
            document.getElementById('success-text').innerHTML = `Successfully shortened! Go to <a href="${location.href}redirect/${shortcode}">${location.href}redirect/${shortcode}</a> to redirect. The shortcode for stats is ${shortcode}.`
        }
        console.log(resp.body);
        
    } catch (error) {
        console.error(error.message);
    }
}

function statsBtnClicked() {
    const shortcode = document.getElementById('short-code').value;
    if (shortcode === '' || shortcode === null) {
        document.getElementById('err-text').innerHTML = `Encountered an error: No shortcode entered`;
        return;
    }
    document.getElementById('err-text').innerHTML = '';
    document.getElementById('success-text').innerHTML = '';
    window.location.href = BASE_URL + 'stats/' + shortcode;
}

function statsPageLoad() {
    const shortcode = new URLSearchParams(window.location.search).get('shortcode');
    if (shortcode === '' || shortcode === null) {
        document.getElementById('error').classList.toggle('hide');
        document.getElementById('err-text').innerHTML = `Encountered an error: No shortcode entered`;
        return;
    }
    document.getElementById('err-text').innerHTML = '';
    document.getElementById('success-text').innerHTML = '';
    document.getElementById('shortcode').innerHTML = shortcode;
}