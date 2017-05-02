'use strict';

angular.module('account', ['common']);


angular.module('account').component('account', {
    templateUrl: '/static/html/account-list.html',

    controller: function (Post, $cookies, $location, $routeParams, $rootScope, $scope, $http) {
        $scope.currencies = ['USD', 'RUB', 'GBP', 'EUR', 'CHF'];


        $scope.changeCols = function (number) {
            if (angular.isNumber(number)) {
                $scope.numCols = number
            } else {
                $scope.numCols = 2
            }
            setupCol($scope.items, $scope.numCols)
        };

        $scope.loadingQuery = false;
        $scope.$watch(function () {
            if ($scope.query) {
                $scope.loadingQuery = true;
                $scope.cssClass = 'col-sm-12';
                if ($scope.query != q) {
                    $scope.didPerformSearch = false;
                }
            } else {
                if ($scope.loadingQuery) {
                    setupCol($scope.items, 2);
                    $scope.loadingQuery = false
                }
            }
        });

        function setupCol(data, number) {
            if (angular.isNumber(number)) {
                $scope.numCols = number
            } else {
                $scope.numCols = 2
            }
            $scope.cssClass = 'col-sm-' + (12 / $scope.numCols);
            $scope.items = data;
            $scope.colItems = chunkArrayInGroups(data, $scope.numCols)
        }

        function fillAccounts() {
            Post.query(function (data) {
                setupCol(data, 2)
            }, function (errorData) {
                var t = 4
            });
        }

        fillAccounts();

        function chunkArrayInGroups(array, unit) {
            var results = [],
                length = Math.ceil(array.length / unit);
            for (var i = 0; i < length; i++) {
                results.push(array.slice(i * unit, (i + 1) * unit));
            }
            return results;
        }


        function init_newAccount() {
            $scope.newAccount = {};
            $scope.newAccount.open = false;
            $scope.accountError = {}
        }

        init_newAccount();

        $scope.addNewAccount = function () {
            if (!$scope.newAccount.currency) {
                $scope.accountError.currencyError = ["This field is required."]

            }
            if ($scope.newAccount.currency) {
                var reqConfig = {
                    method: "POST",
                    url: "/api/accounts/",
                    data: {
                        currency: $scope.newAccount.currency
                    }
                };
                var requestAction = $http(reqConfig);

                requestAction.success(function (r_data, r_status, r_headers, r_config) {
                    $scope.log = "Account create with number " + r_data.data["accountId"];
                    fillAccounts();
                    init_newAccount();
                });
                requestAction.error(function (e_data, e_status, e_headers, e_config) {
                    // console.log(e_data) // error
                    $scope.log = e_data.data["message"]

                })
            }

        }
    }
});