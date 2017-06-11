import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { AuctionViewComponent } from './auction-view.component';
import { AuctionService } from './auction.service';

@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        HttpModule,
        RouterModule.forRoot([
            {
                path: 'auction/:id',
                component: AuctionViewComponent
            },
        ])
    ],
    declarations: [
        AppComponent,
        AuctionViewComponent,
    ],
    providers: [
        AuctionService,
    ],
    bootstrap: [AppComponent]
})


export class AppModule {
}
