import { Component } from '@angular/core';

import { AuctionService } from './auction.service'

@Component({
    selector: 'app-root',
    template: `
    <router-outlet></router-outlet>
    `,
    providers: [AuctionService]
})
export class AppComponent {
}
