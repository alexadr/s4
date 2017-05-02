'use strict';

angular.module('accountdetails', ['common']);

angular.module('accountdetails').component('accountdetails', {
    templateUrl: "/static/html/account-details.html",

    controller: function (Post, AccountList, Transaction, $cookies, $location, $routeParams, $rootScope, $scope, $filter, $http) {
        if ($cookies.get("csrftoken")) {
            $scope.csrftoken = $cookies.get("csrftoken")
        }

        function postDataSuccess(data) {
            $scope.loading = false;
            $scope.post = data
        }

        function postDataError(e_data) {
            $scope.loading = false;
            if (e_data.status == 404) {
                $scope.notFound = true;
            } else {
                // status code 500
                $scope.pageError = true;
            }
        }

        var slug = $routeParams.slug;


        function initTransactionHistory() {
            Post.get({"slug": slug}, postDataSuccess, postDataError);
        }

        initTransactionHistory();

        AccountList.query(function (data) {
            $scope.accounts = data
        }, function (errorData) {
            console.log(errorData)
        });

        $scope.transferClass = function (scores) {
            return scores.type == 'W' ? 'outcome' : 'income';
        };

        $scope.$watch('newTransaction.destination', function (newValue, oldValue) {
            if (newValue != oldValue) {
                var found = $filter('filter')($scope.accounts, {number: newValue}, true);
                $scope.newTransaction.destCurrency = found[0].currency;
                make_conversion()
            }
        });

        $scope.$watch('newTransaction.total', function (newValue, oldValue) {
            if (newValue != oldValue) {
                make_conversion()
            }
        });

        function make_conversion() {
            if ($scope.newTransaction && $scope.newTransaction.destination) {

                if ($scope.post.currency != $scope.newTransaction.destCurrency && $scope.newTransaction.total && $scope.newTransaction.total > 0) {
                    var reqConfig = {
                        method: "GET",
                        url: 'http://api.fixer.io/latest',
                        params: {'base': $scope.post.currency, 'symbols': $scope.newTransaction.destCurrency}
                    };
                    var requestAction = $http(reqConfig);

                    requestAction.success(function (data, r_status, r_headers, r_config) {

                        $scope.newTransaction.conversion = $scope.newTransaction.total * data["rates"][$scope.newTransaction.destCurrency];
                    });
                    requestAction.error(function (e_data, e_status, e_headers, e_config) {
                        // console.log(e_data) // error
                        $scope.loginError = e_data

                    })
                } else {
                    $scope.newTransaction.conversion = $scope.newTransaction.total
                }
            }
        }

        function init_newTransaction() {
            $scope.newTransaction = {};
            $scope.newTransaction.open = false;
            $scope.transactionError = {};
            $scope.newTransaction.log = ""
        }

        init_newTransaction();

        $scope.addNewTransaction = function () {
            $scope.newTransaction.log = "";
            $scope.transactionError = {};
            if (!$scope.newTransaction.comment) {
                $scope.transactionError.commentError = ["This field may not be blank."]
            }
            if (!$scope.newTransaction.destination) {
                $scope.transactionError.destinationError = ["This field may not be blank."]
            }
            // console.log($scope.reply)
            if (!$scope.newTransaction.total) {
                $scope.transactionError.totalError = ["This field is required."]
            } else {
                Transaction.create({
                    source: $scope.post.number,
                    destination: $scope.newTransaction.destination,
                    total: $scope.newTransaction.total,
                    comment: $scope.newTransaction.comment,
                    slug: slug,
                    type: "post"
                }, function (data) {

                    initTransactionHistory();
                    init_newTransaction();
                    $scope.newTransaction.log = "Transaction was created "
                }, function (e_data) {
                    init_newTransaction();
                    $scope.newTransaction.log = e_data.data["message"]
                })
            }

        }

    }
});