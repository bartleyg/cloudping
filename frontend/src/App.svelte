<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { DateTime } from 'luxon';
  import { v4 as uuid4 } from 'uuid';

  import Spinner from "./Spinner.svelte";

	const API_URL = "https://cloud-ping-api-vlvkei3cma-uk.a.run.app/api";

  let pingHistory = [];
	let endpoints = [];
  let pingSequence = [];
  let pingInProcess = false;
  let browserId = null;

  onMount(async () => {
    getPingHistory().then(data => pingHistory = data);
    getEndpoints().then(data => endpoints = data);
    // get or set a browser id
    browserId = localStorage.getItem("browserId");
    if (browserId == null) {
      browserId = uuid4();
      localStorage.setItem("browserId", browserId);
    }
  });

  // format date in ping history table once udpated
  $: pingHistory.map(p => {
      p.date = DateTime.fromISO(p.date).toLocaleString(DateTime.DATETIME_SHORT);
    });

	function getPingHistory() {
    return axios.get(`${API_URL}/pings`)
      .then(response => {
        if (response.data.error) {
          console.log('ERROR /pings:', response.data.error);
        } else {
          return response.data;
        }
      })
      .catch(error => console.log('ERROR /pings:', error));
	}

	function getEndpoints() {
		return axios.get(`${API_URL}/endpoints`)
			.then(response => {
        if (response.data.error) {
          console.log('ERROR /endpoints:', response.data.error);
        } else {
          return response.data;
        }
			})
			.catch(error => console.log('ERROR /endpoints:', error));
	}

	async function startPing() {
		let type = "lowest_single";
    // clear old pings
    pingSequence = [];
    pingInProcess = true;
    // ping all endpoints and wait
		let endpointsPing = await pingAll();

		// build ping object for display and get best ping
		let lowest_duration = Number.MAX_SAFE_INTEGER;
		let best_ping = null;
		for (let e of endpoints) {
      // build one ping of pingSequence for display
      let duration = endpointsPing[e.id];
      pingSequence.push({
        "protocol": e.protocol,
        "cloud": e.cloud,
        "region": e.region,
        "location": e.location,
        "duration": duration,
      });
      // get best ping in format for DB
			if (duration < lowest_duration) {
		    best_ping = {
		        "user": browserId,
		        "type": type,
		        "endpoint_id": e.id,
		        "duration": duration,
		    }
				lowest_duration = duration;
			}
		}
    // sort by lowest ping
    pingSequence.sort((a, b) => (a.duration > b.duration) ? 1: -1);
		// save best ping to DB
		if (best_ping) {
			postPing(best_ping);
		}
    // clear spinnner
    pingInProcess = false;
	}

	function postPing(ping) {
		let payload = [ping]
		return axios.post(`${API_URL}/pings`, payload)
			.then(response => {
        if (response.data.error) {
          console.log('ERROR /pings:', response.data.error);
        } else {
          return response.data;
        }
			})
			.catch(error => console.log('ERROR /pings:', error));
	}

	async function pingAll() {
		let endpointsPing = {};
		let allStart = Date.now();
		return Promise.all(endpoints.map(async e => {
			let start = Date.now();
			await fetch(e.url, {mode: "no-cors"});
			let pingMs = Date.now() - start; // only ms (int) precision
			endpointsPing[e.id] = pingMs;
		})).then(() => {
      let allPingMS = Date.now() - allStart;
			console.log(`pingAll took ${allPingMS} ms`);
			return endpointsPing;
		});
	}
</script>

<main>
	<article>
		<h1>Cloud Ping</h1>
		<h2>Ping all the cloud providers.</h2>
		<p>Amazon AWS, Google GCP, Microsoft Azure</p>
    {#if pingInProcess}
      <Spinner/>
    {:else}
		  <button on:click={startPing} class="button">PING</button>
    {/if}
		{#if pingSequence.length > 0}
			<table>
        <caption><h2>Your Ping Results</h2></caption>
				<thead>
					<tr>
						<th>Cloud</th>
						<th>Region</th>
						<th>Location</th>
						<th>Duration</th>
					</tr>
				</thead>
				<tbody>
				{#each pingSequence as p}
					<tr>
						<td>{p.cloud}</td>
						<td>{p.region}</td>
						<td>{p.location}</td>
						<td>{p.duration} ms</td>
					</tr>
				{/each}
				</tbody>
			</table>
		{/if}
		{#if pingHistory.length > 0}
			<table>
        <caption><h2>Best Ping Results History</h2></caption>
				<thead>
					<tr>
						<th>Date</th>
						<th>Protocol</th>
						<th>Cloud</th>
						<th>Region</th>
						<th>Location</th>
						<th>Duration</th>
					</tr>
				</thead>
				<tbody>
				{#each pingHistory as p}
					<tr>
						<td>{p.date}</td>
						<td>{p.protocol}</td>
						<td>{p.cloud}</td>
						<td>{p.region}</td>
						<td>{p.location}</td>
						<td>{p.duration} ms</td>
					</tr>
				{/each}
				</tbody>
			</table>
		{/if}
    <p class="footer">
      <a href="https://bartleygillan.com" target="_blank" rel="noopener noreferrer">
        Made with
        <span role="img" aria-label="brain">🧠</span>
        &nbsp;by Bartley Gillan
      </a>
    </p>
	</article>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}

	table {
	    border-collapse: collapse;
	    margin: 25px auto;
	    font-size: 0.9em;
	    font-family: sans-serif;
	    min-width: 400px;
	    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
	}
	thead tr {
    background-color: #009879;
    color: #ffffff;
    text-align: left;
	}
	th, td {
    text-align: center;
    padding: 12px 15px;
	}
	table tbody tr {
	    border-bottom: 1px solid #dddddd;
	}
	table tbody tr:nth-of-type(even) {
	    background-color: #f3f3f3;
	}
	table tbody tr:last-of-type {
	    border-bottom: 2px solid #009879;
	}

  .button {
    margin-top: 1em;
    color: #ff3e00;
    font-size: 30px;
    border-radius: 20px;
  }

  .footer {
    font-size: 12px;
    margin-top: 30px;
  }
</style>
