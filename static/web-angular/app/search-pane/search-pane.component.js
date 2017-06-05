/**
 * Created by jsz on 2017/4/18
 */
'use strict'
angular.
    module('searchPane').
    component('searchPaneCom', {
        templateUrl: 'search-pane/search-pane.template.html',
        controller: ['$scope', '$state', '$http',
            function SearchController($scope, $state, $http) {

                jQuery('#results').dataTable({
                    "searching": false,
                    "destroy": true,
                    "lengthChange": false,
                    "columns": [
                        {'data': 'isbn'}, 
                        {'data': 'book_title'}, 
                        {'data': 'book_author'}, 
                        {'data': 'publisher'}, 
                        {'data': 'year_of_publication'} 
                    ]
                });

                var facet_dict = [];
                var init_facet_data = function init_facet_data(which){
                    if(which == 'publisher'){
                        angular.element('#publisher').addClass('active');
                        angular.element('#author').removeClass('active');
                        angular.element('#year').removeClass('active');
                        $scope.values = facet_dict['Publisher'];                
                    }else if(which == 'author'){
                        angular.element('#author').addClass('active');
                        angular.element('#publisher').removeClass('active');
                        angular.element('#year').removeClass('active');
                        $scope.values = facet_dict['Book_Author'];        
                    }else if(which == 'year'){
                        angular.element('#year').addClass('active');
                        angular.element('#author').removeClass('active');
                        angular.element('#publisher').removeClass('active');
                        $scope.values = facet_dict['Year_Of_Publication'];            
                   }       
                };
                $scope.init_facet_data = init_facet_data;
                init_facet_data('publisher');

                $scope.key_words_search = function(key_words){
                    var key_words = angular.copy(key_words);
                    if(key_words != ''){
                        $http({
                            method: 'GET',
                            url: '/keyWordsSearch',
                            params: {'key_words': key_words}
                        }).success(function(data, status, headers, config){
                            jQuery('#results').dataTable({
                                 "destroy": true,
                                 'data': data.content,
                                 "searching": false,
                                 "lengthChange": false,
                                 "columns": [
                                    {'data': 'isbn'}, 
                                    {'data': 'book_title'}, 
                                    {'data': 'book_author'}, 
                                    {'data': 'publisher'}, 
                                    {'data': 'year_of_publication'} 
                                 ]
                            });
                            $scope.facets = data.facets
                            for (var i = 0; i< $scope.facets.length; i++){
                                facet_dict[$scope.facets[i].facet_name] = $scope.facets[i].values;
                            }
                            init_facet_data('publisher')
                        }); 
                    }
                };

                $scope.facet_search = function(new_attr){
                    facet_dict = []
                    init_facet_data('publisher')

                    var new_attr = angular.copy(new_attr);
                    if(new_attr != ''){
                        $http({
                            method: 'GET',
                            url: '/facetSearch',
                            params: {'new_attr': new_attr}
                        }).success(function(data, status, headers, config){
                            jQuery('#results').dataTable({
                                 "destroy": true,
                                 'data': data.content,
                                 "searching": false,
                                 "lengthChange": false,
                                 "columns": [
                                    {'data': 'isbn'}, 
                                    {'data': 'book_title'}, 
                                    {'data': 'book_author'}, 
                                    {'data': 'publisher'}, 
                                    {'data': 'year_of_publication'} 
                                 ]
                            });
                            $scope.facets = data.facets
                            for (var i = 0; i< $scope.facets.length; i++){
                                facet_dict[$scope.facets[i].facet_name] = $scope.facets[i].values;
                            }
                            init_facet_data('publisher')
                        });
                    }
                };
            }
        ]
    });
