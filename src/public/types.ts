export interface ICurrentSongResponse {
  actions: any;
  context: any;
  currently_playing_type: string;
  is_playing: boolean;
  item: ISpotifyTrack;
  progress_ms: number;
  timestamp: number;
}

export interface ISpotifyTrack {
  album: {
    album_type: string;
    artists: {
      external_urls: {
        [propName: string]: string;
      };
      href: string;
      id: string;
      name: string;
      type: string;
      uri: string;
    }[];
    available_markets: string[];

    external_urls: {
      [propName: string]: string;
    };
    href: string;
    id: string;
    images: {
      height: number;
      url: string;
      width: number;
    }[];
    name: string;
    release_date: string;
    release_date_precision: string;
    type: string;
    uri: string;
  };
  artists: {
    external_urls: {
      [propName: string]: string;
    };
    href: string;
    id: string;
    name: string;
    type: string;
    uri: string;
  }[];
  available_markets: string[];
  disc_number: number;
  duration_ms: number;
  explicit: boolean;
  external_ids: {
    isrc?: string;
  };
  external_urls: {
    [propName: string]: string;
  };
  href: string;
  id: string;
  is_local: boolean;
  name: string;
  popularity: number;
  preview_url: string;
  track_number: number;
  type: string;
  uri: string;
}
