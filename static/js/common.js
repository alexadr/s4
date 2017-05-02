var m = angular.module('common',['ngCookies']);

m.factory("LoginRequiredInterceptor", function($cookies, $location){
                return function(response){
                        console.log("working");
                        //console.log("interceptor error")
                        //console.log(response)
                        if (response.status == 403){
                            var currentPath = $location.path();
                            console.log(currentPath);
                            if (currentPath == "/login") {
                                $location.path("/login")
                            } else {
                                $location.path("/login").search("next", currentPath)
                            }
                        }
                    }
        });

m.factory('Post', function($resource,LoginRequiredInterceptor){
            var url = '/api/accounts/:slug/';
            return $resource(url, {}, {
                query: {
                    method: "GET",
                    params: {},
                    isArray: true,
                    cache: false,
                    transformResponse: function(data, headersGetter, status){
                        // console.log(data)
                        var finalData = angular.fromJson(data);
                        return finalData.results
                    },
                    interceptor: {responseError: LoginRequiredInterceptor}

                },
                get: {
                    method: "GET",
                    params: {"slug": "@slug"},
                    isArray: false,
                    cache: false,
                    interceptor: {responseError: LoginRequiredInterceptor}
                }
            })

        });
m.factory('AccountList', function($resource,LoginRequiredInterceptor){
            var url = '/api/accountlist/';
            return $resource(url, {}, {
                query: {
                    method: "GET",
                    params: {},
                    isArray: true,
                    cache: false,
                    transformResponse: function(data, headersGetter, status){
                        // console.log(data)
                        var finalData = angular.fromJson(data);
                        return finalData.results
                    },
                    interceptor: {responseError: LoginRequiredInterceptor}

                }
            })

        });



m.factory('Transaction', function( $cookies, $httpParamSerializer, $location, $resource){
            var url = '/api/transactions/:id/';
            var commentQuery = {
                url: url,
                method: "GET",
                params: {},
                isArray: true,
                cache: false,
                transformResponse: function(data, headersGetter, status){
                    // console.log(data)
                    var finalData = angular.fromJson(data);
                    return finalData.results
                }
            };

            var commentGet = {
                    method: "GET",
                    params: {"id": "@id"},
                    isArray: false,
                    cache: false

                };

             var commentCreate = {
                    url: '/api/transactions/',
                    method: "POST"

                };

            var token = $cookies.get("token");
            if (token){
                commentCreate["headers"] = {"Authorization": "JWT " + token}

            }

            return $resource(url, {}, {
                query: commentQuery,
                get: commentGet,
                create: commentCreate
            })

        });