(()=>{"use strict";var e,t={7172:(e,t,i)=>{var n,r,a,c,o,s,l,d,f=i(1743),p=i(7130),h=i(1927),u=i(8021),b=i(1454),x=i.n(b),g=i(7654),y=i(8131),v=i(3432),_=(i(3894),i(1783));i(2001);function w(e,t,i,n){i&&Object.defineProperty(e,t,{enumerable:i.enumerable,configurable:i.configurable,writable:i.writable,value:i.initializer?i.initializer.call(n):void 0})}function S(e,t,i,n,r){var a={};return Object.keys(n).forEach((function(e){a[e]=n[e]})),a.enumerable=!!a.enumerable,a.configurable=!!a.configurable,("value"in a||a.initializer)&&(a.writable=!0),a=i.slice().reverse().reduce((function(i,n){return n(e,t,i)||i}),a),r&&void 0!==a.initializer&&(a.value=a.initializer?a.initializer.call(r):void 0,a.initializer=void 0),void 0===a.initializer?(Object.defineProperty(e,t,a),null):a}n=(0,u.EM)("firefox-condition"),r=(0,u.MZ)({attribute:!1}),a=(0,u.MZ)({attribute:!1}),n(((d=class extends h.WF{constructor(...e){super(...e),w(this,"onSwitch",s,this),w(this,"onActionClick",l,this),this.isOn=!1,this.label="",this.text="",this.actionText=""}static get properties(){return{isOn:{type:Boolean},label:{type:String},text:{type:String},actionText:{type:String}}}render(){return h.qy`
      <div>
        <div class="Sub_header">${this.label}</div>
        <div class="FF_switch_row">
          <div class="Text">
            ${this.text}<span class="FF_Link" @click="${this.onActionClick}"
              >${(0,_._)(this.actionText)}</span
            >
          </div>
          <div>
            <checkbox-switch .checked="${this.isOn}" @click="${this.onSwitch}">
            </checkbox-switch>
          </div>
        </div>
      </div>
    `}}).styles=h.AH`
    .Text {
      font-family: Open Sans;
      letter-spacing: -0.41px;
      color: #616675;
      margin-bottom: 0px;
      color: #616675;
      font-size: 12px;
      font-weight: 400;
      line-height: 17px;
      word-wrap: break-word;
      text-align: left;
    }
    .Text a {
      color: #007aff;
      text-decoration: none;
    }
    .Link {
      font-size: 16px;
      line-height: 1.4;
      letter-spacing: -0.41px;
      font-weight: 400;
      text-align: center;
      margin-bottom: 0px;
      color: #007aff;
      text-decoration: none;
      cursor: pointer;
    }

    .Sub_header {
      color: #616675;
      font-size: 15px;
      font-family: Open Sans;
      font-weight: 600;
      line-height: 17px;
      word-wrap: break-word;
      text-align: left;
      margin: 12px 0;
    }

    .FF_Link {
      font-weight: 400;
      text-align: center;
      color: #007aff;
      text-decoration: none;
      cursor: pointer;
    }

    .FF_switch_row {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 15px;
    }
  `,s=S((o=d).prototype,"onSwitch",[r],{configurable:!0,enumerable:!0,writable:!0,initializer:function(){return()=>{}}}),l=S(o.prototype,"onActionClick",[a],{configurable:!0,enumerable:!0,writable:!0,initializer:function(){return()=>{}}}),c=o));var k,m;const F=Object.fromEntries(Object.entries({ffScreenPrivacyChoicesHeader:"ff_screen_privacy_choices_header",ffScreenPrivacyChoicesText:"ff_screen_privacy_choices_text",ffScreenStatisticalDataHeader:"ff_screen_statistical_data_header",ffScreenStatisticalDataText:"ff_screen_statistical_data_text",ffScreenIdentifiersHeader:"ff_screen_identifiers_header",ffScreenIdentifiersText:"ff_screen_identifiers_text",ffScreenPrivacyPolicyLinkText:"ff_screen_privacy_policy_link_text",ffScreenPrivacyPolicyLinkUrl:"ff_screen_privacy_policy_link_url",ffClickAccept:"click_accept_terms_and_conditions"}).map((([e,t])=>[e,(0,p.A)(t)])));(0,u.EM)("firefox-terms-and-conditions")(((m=class extends h.WF{constructor(){super(),this.acceptedIdentifiers=!1,this.acceptedStatisticalData=!0,this.source="unknown"}static get properties(){return{acceptedIdentifiers:{type:Boolean,state:!0},acceptedStatisticalData:{type:Boolean,state:!0}}}changeIdentifiers(){this.acceptedIdentifiers=!this.acceptedIdentifiers}async changeStatisticalData(){const e=!this.acceptedStatisticalData,t=!e;await y.A.set("dontSendTelemetry",t),this.acceptedStatisticalData=e}updated(e){var t;const i=null===(t=this.renderRoot)||void 0===t?void 0:t.querySelector("#accept-button");e.has("acceptedIdentifiers")&&(i.disabled=!this.acceptedIdentifiers)}async clickFFPrivacyPolicy(){v.A.track("accept_policy_privacy",{type:"tab",source:this.source}),x().tabs.create(F.ffScreenPrivacyPolicyLinkUrl)}async ffAccept(){const e=this.acceptedIdentifiers;v.A.track("personal_optout",{enabled:e?"1":"0",type:"tab",source:this.source});const t=this.acceptedStatisticalData;v.A.track("telemetry_optout",{enabled:t?"1":"0",type:"tab",source:this.source}),v.A.track("policy_accepted",{type:"tab",source:this.source}),y.A.set(g.O.startupConditionsAcceptedShown,!0),y.A.set(g.O.startupAcceptConditionsPhase,2),window.close()}async firstUpdated(){this.source=await y.A.get(g.O.firefoxPolicyTabOpenedSource),v.A.track("accept_policy_view",{type:"tab",source:this.source})}render(){return h.qy`
      <tab-header></tab-header>
      <div class="FF_screen">
        <div>
          <div class="Main_header">
            ${F.ffScreenPrivacyChoicesHeader}
          </div>
          <div class="Text FF_header_text">
            ${F.ffScreenPrivacyChoicesText}
          </div>
        </div>

        <firefox-condition
          label=${F.ffScreenStatisticalDataHeader}
          text=${F.ffScreenStatisticalDataText}
          actionText=${F.ffScreenPrivacyPolicyLinkText}
          .onActionClick=${this.clickFFPrivacyPolicy.bind(this)}
          .isOn=${this.acceptedStatisticalData}
          .onSwitch=${this.changeStatisticalData.bind(this)}
        ></firefox-condition>

        <firefox-condition
          label=${F.ffScreenIdentifiersHeader}
          text=${F.ffScreenIdentifiersText}
          actionText=${F.ffScreenPrivacyPolicyLinkText}
          .onActionClick=${this.clickFFPrivacyPolicy.bind(this)}
          .isOn=${this.acceptedIdentifiers}
          .onSwitch=${this.changeIdentifiers.bind(this)}
        ></firefox-condition>

        <div class="Button">
          <input
            type="button"
            id="accept-button"
            value="${F.ffClickAccept}"
            @click="${this.ffAccept}"
            .disabled=${!0}
          />
        </div>
      </div>
    `}}).styles=h.AH`
    :host {
      display: block;
      position: absolute;
      top: 0px;
      left: 0;
      width: 100%;
      height: 100vh;
      background: white;
      font-size: 14px;
      z-index: 999;
    }

    :host > .In {
      position: absolute;
      bottom: 20px;
      left: 0;
      right: 0;
      text-align: center;
    }

    .Button {
      text-align: center;
      padding-top: 82px;
      box-sizing: border-box;
      width: 100%;
      padding-left: 25px;
      padding-right: 25px;
    }
    .Button input {
      display: block;
      width: 100%;
      margin: 0;
      box-sizing: border-box;
      height: 60px;
      line-height: 100%;
      border: 0;
      cursor: pointer;
      min-width: 200px;
      background: var(--brand-green);
      text-align: center;
      border-radius: 4px;
      color: #fff;
      font-size: 18px;
      font-weight: 600;
    }

    .Button input:disabled,
    input[disabled] {
      background: #e2e2e2;
      cursor: not-allowed;
    }

    .FF_screen {
      height: 520px;
      width: 640px;
      margin: 0 auto;
      text-align: center;

      padding: 80px 25px 0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: start;
    }
    .FF_screen .Main_header {
      color: #616675;
      font-size: 18px;
      font-family: Open Sans;
      font-weight: 600;
      line-height: 22px;
      word-wrap: break-word;
      text-align: left;
      margin-bottom: 12px;
    }

    .FF_screen .Text {
      font-family: Open Sans;
      color: #616675;
      font-size: 12px;
      font-weight: 400;
      line-height: 17px;
      word-wrap: break-word;
      text-align: left;
    }

    .FF_screen > .Button {
      text-align: center;
      padding-top: 8px;
      box-sizing: border-box;
      width: 100%;
      padding-left: 0px;
      padding-right: 0px;
    }
    .FF_screen .Button input {
      display: block;
      width: 100%;
      margin: 0;
      box-sizing: border-box;
      height: 60px;
      line-height: 100%;
      border: 0;
      cursor: pointer;
      min-width: 200px;
      background: var(--brand-green);
      text-align: center;
      border-radius: 4px;
      color: #fff;
      font-size: 18px;
      font-weight: 600;
    }

    .FF_screen > .Button input:disabled,
    input[disabled] {
      background: #e2e2e2;
      cursor: not-allowed;
    }
  `,k=m));document.title=(0,p.A)("terms_and_conditions_ff"),(async()=>{const e=(0,f.A)();window.language=e,document.body.prepend(document.createElement("firefox-terms-and-conditions"))})()}},i={};function n(e){var r=i[e];if(void 0!==r)return r.exports;var a=i[e]={id:e,loaded:!1,exports:{}};return t[e].call(a.exports,a,a.exports,n),a.loaded=!0,a.exports}n.m=t,e=[],n.O=(t,i,r,a)=>{if(!i){var c=1/0;for(d=0;d<e.length;d++){for(var[i,r,a]=e[d],o=!0,s=0;s<i.length;s++)(!1&a||c>=a)&&Object.keys(n.O).every((e=>n.O[e](i[s])))?i.splice(s--,1):(o=!1,a<c&&(c=a));if(o){e.splice(d--,1);var l=r();void 0!==l&&(t=l)}}return t}a=a||0;for(var d=e.length;d>0&&e[d-1][2]>a;d--)e[d]=e[d-1];e[d]=[i,r,a]},n.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return n.d(t,{a:t}),t},n.d=(e,t)=>{for(var i in t)n.o(t,i)&&!n.o(e,i)&&Object.defineProperty(e,i,{enumerable:!0,get:t[i]})},n.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"==typeof window)return window}}(),n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.nmd=e=>(e.paths=[],e.children||(e.children=[]),e),n.j=360,(()=>{var e={360:0};n.O.j=t=>0===e[t];var t=(t,i)=>{var r,a,[c,o,s]=i,l=0;if(c.some((t=>0!==e[t]))){for(r in o)n.o(o,r)&&(n.m[r]=o[r]);if(s)var d=s(n)}for(t&&t(i);l<c.length;l++)a=c[l],n.o(e,a)&&e[a]&&e[a][0](),e[a]=0;return n.O(d)},i=self.webpackChunkbrowsec_extension=self.webpackChunkbrowsec_extension||[];i.forEach(t.bind(null,0)),i.push=t.bind(null,i.push.bind(i))})();var r=n.O(void 0,[76],(()=>n(7172)));r=n.O(r)})();