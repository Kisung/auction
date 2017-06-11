import { checkAndUpdatePureExpressionInline } from '@angular/core/src/view/pure_expression';
import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { Http, Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/catch';

import { Auction, Bid } from './models';
import { AuctionService } from './auction.service';

@Component({
    selector: 'app-root',
    templateUrl: './auction-view.component.html',
    styleUrls: ['./app.component.css'],
    providers: [AuctionService]
})
export class AuctionViewComponent implements OnInit {

    auction: Auction;
    bid: Bid = new Bid(0, null, null, 1000);

    constructor(
        private auctionService: AuctionService,
        private route: ActivatedRoute,
        private http: Http) {
    }

    ngOnInit(): void {
        this.route.params
            .map(params => params['id'])
            .switchMap(id => this.auctionService.getRecord(id))
            .subscribe(auction => (this.auction = auction, this.bid.auction_id = auction.id));
        ;
    }

    onSubmit() {
        this.auctionService.postBid(this.bid).subscribe(bid => (this.bid = bid, console.log(bid)));
    }

    // TODO: Remove this when we're done
    get diagnostic() { return JSON.stringify(this.auction); }
}

