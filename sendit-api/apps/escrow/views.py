from rest_framewrk.views import APIView
from rest_framework.response import Response


# class WalletView(APIView):

#     def get(self, request):
#         data = WalletService.get_breakdown(request.user)
#         return Response(data)


# class WalletHistoryView(APIView):

#     def get(self, request):

#         entries = WalletService.get_history(request.user)

#         serializer = LedgerSerializer(entries, many=True)
#         return Response(serializer.data)
