import { ICurrentSongResponse } from "./types";
import Vibrant from "node-vibrant";
import axios from "axios";

async function getToken(): Promise<string> {
  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");
  const state = params.get("state");
  const refreshToken = localStorage.getItem("refreshToken");
  if (!refreshToken) {
    const { access_token: token, refresh_token: refreshToken } = (await axios.get(
      `/get-token?code=${code}&state=${state}`
    )).data;
    localStorage.setItem("refreshToken", refreshToken);
    return token;
  }
  const { access_token: token } = (await axios.get(
    `/refresh-token?refresh_token=${refreshToken}`
  )).data;
  return token;
}

async function getCurrentSong(token: string): Promise<ICurrentSongResponse> {
  let response;
  try {
    response = await axios.get(`/api/current-song?token=${token}`);
  } catch (error) {
    if (error.response && error.response.status !== 204) window.location.replace("/");
    return;
  }
  const currentSong = response.data;
  return currentSong;
}

async function getLyrics(artist, title): Promise<string> {
  let response;
  try {
    response = await axios.get(`/api/lyrics?artist=${artist}&title=${title}`);
  } catch (error) {
    if (error.response && error.response.status !== 204) window.location.replace("/");
    return;
  }
  const lyrics = response.data;
  return lyrics;
}

async function wait(time: number) {
  return new Promise(resolve => {
    setTimeout(resolve, time);
  });
}

async function displayLyrics(artists: string[], title: string, lyrics: string, cover: string) {
  const section = document.querySelector("section");
  section.style.opacity = "0";
  await wait(1000);
  document.querySelector(".title").textContent = title;
  document.querySelector(".artists").textContent = artists.map(artist => artist).join(", ");
  document.querySelector(".lyrics").innerHTML = buildParagraphs(lyrics);
  (document.getElementById("cover") as HTMLImageElement).src = cover;
  const palette = await Vibrant.from(cover).getPalette();
  const colorPair = [palette.LightVibrant.getHex(), palette.DarkVibrant.getHex()];
  getBackground(colorPair);
  section.style.opacity = "1";
}

function getBackground(colorPair: string[]) {
  const body = document.querySelector("body");
  const s = `linear-gradient(to bottom right, ${colorPair[0]} 0%, ${colorPair[1]} 100%)`;
  body.style.background = s;
  body.style.color = "white";
}

function buildParagraphs(lyrics: string): string {
  lyrics = lyrics.trim();
  if (lyrics.length === 0) return "Lyrics not available";
  const paras = lyrics.split("\n");
  const result = paras.join("</br>");
  return result;
}

async function main() {
  let token: string;
  try {
    token = await getToken();
  } catch {
    return window.location.replace("/");
  }
  let currentSong: ICurrentSongResponse;
  let oldSOng: ICurrentSongResponse;
  const timeToWait = 0.5 * 1000;

  let numTries = 0;
  while (!currentSong && numTries <= 5) {
    await wait(timeToWait);
    currentSong = await getCurrentSong(token);
    numTries += 1;
  }

  let artists;
  let artist;
  let title;
  let lyrics;
  let cover;

  if (!currentSong) {
    artists = ["Artist not Found"];
    artist = artists[0];
    title = "Song not Found";
    lyrics = "";
    cover = "https://i.scdn.co/image/276cd871d7750e9a002aada5237e328798b53650";
  } else {
    artists = currentSong.item.artists.map(o => o.name);
    artist = artists[0];
    title = currentSong.item.name;
    lyrics = await getLyrics(artist, title);
    cover = currentSong.item.album.images[0].url;
  }

  await displayLyrics(artists, title, lyrics, cover);
  (document.querySelector(".loader") as HTMLDivElement).style.display = "none";
  oldSOng = currentSong;

  while (true) {
    await wait(timeToWait);
    currentSong = await getCurrentSong(token);
    if (!currentSong || !currentSong.item) continue;
    const artists = currentSong.item.artists.map(o => o.name);
    const artist = artists[0];
    const title = currentSong.item.name;
    if (oldSOng && oldSOng.item.name === title && oldSOng.item.artists[0].name === artist) {
      continue;
    }
    const lyrics = await getLyrics(artist, title);
    const cover = currentSong.item.album.images[0].url;
    await displayLyrics(artists, title, lyrics, cover);
    oldSOng = currentSong;
  }
}

main();
