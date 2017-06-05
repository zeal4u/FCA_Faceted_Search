/**
 * Created by jsz on 2016/10/20.
 * this this route of website
 */
'use strict';
angular.
  module('facetSearchApp').
  config(['$stateProvider', '$urlServiceProvider',
    function ($stateProvider, $urlServiceProvider) {
        $stateProvider.
            state('search', {
                name: 'search',
                url: '/search',
                views: {
                        main:{
                            component: 'searchPaneCom'
                        } 
                }
            });
       $urlServiceProvider.rules.otherwise({state: 'search'});
   }]
  );
