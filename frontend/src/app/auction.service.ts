import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';

import { Auction, Bid } from './models';

@Injectable()
export class AuctionService {
    public host = 'http://localhost:8003';

    constructor(private http: Http) { }

    getRecord(id: number): Observable<Auction> {
        return this.http
            .get(this.host + '/api/v1/auction/' + id)
            .map((resp: Response) => resp.json());
    }

    postBid(bid: Bid): Observable<Bid> {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });
        let url = this.host + '/api/v1/bid';
        let resp = this.http
            .post(url, bid)
            .map(this.extractData);
        console.log(url, resp);
        return resp;
    }

    private extractData(res: Response) {
        let body = res.json();
        return body || {};
    }
}
